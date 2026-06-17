from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from django.conf import settings
from django.dispatch import receiver
from datasets import models as ds
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from core.tasks import async_download_and_update

import datetime as _dt
import os
import csv
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode
from django.utils.timezone import make_aware

from datasets.utils import dates
logger = logging.getLogger('app')


class AcrisRealLegal(BaseDatasetModel, models.Model):
    API_ID = '8h5j-fqxa'
    # Socrata /resource/ endpoint with SoQL filter — see AcrisRealMaster for
    # the rationale. Legal has no docdate/modified_date columns, so we filter
    # on the Socrata system :updated_at column only.
    base_download_endpoint = 'https://data.cityofnewyork.us/resource/8h5j-fqxa.csv'
    SOCRATA_LOOKBACK_DAYS = 120
    QUERY_DATE_KEY = 'documentid__docdate'  # date is on the acrisrealmaster record

    class Meta:
        indexes = [
            models.Index(fields=['bbl', 'documentid']),
            models.Index(fields=['documentid', 'bbl']),

        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    documentid = models.ForeignKey('AcrisRealMaster', db_column='documentid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    recordtype = models.TextField(blank=True, null=True)
    borough = models.SmallIntegerField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    easement = models.BooleanField(blank=True, null=True)
    partiallot = models.TextField(blank=True, null=True)
    airrights = models.BooleanField(blank=True, null=True)
    subterraneanrights = models.BooleanField(blank=True, null=True)
    propertytype = models.TextField(blank=True, null=True)
    streetnumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    goodthroughdate = models.DateField(blank=True, null=True)

    slim_query_fields = ["bbl", "documentid"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(cls, endpoint=None, file_name=None):
        if endpoint is None:
            endpoint = cls._build_socrata_url()
        logger.info("Downloading AcrisRealLegal (filtered): %s", endpoint)
        return cls.download_file(endpoint, file_name=file_name)

    @classmethod
    def _build_socrata_url(cls):
        cutoff = (_dt.date.today() - _dt.timedelta(days=cls.SOCRATA_LOOKBACK_DAYS)).isoformat()
        # See AcrisRealMaster._build_socrata_url for the aliasing rationale.
        select = ','.join([
            'document_id AS documentid',
            'record_type AS recordtype',
            'borough AS borough',
            'block AS block',
            'lot AS lot',
            'easement AS easement',
            'partial_lot AS partiallot',
            'air_rights AS airrights',
            'subterranean_rights AS subterraneanrights',
            'property_type AS propertytype',
            'street_number AS streetnumber',
            'street_name AS streetname',
            'unit AS unit',
            'good_through_date AS goodthroughdate',
        ])
        # No modified_date column on the Legal resource; :updated_at is all we
        # have. Sufficient because Socrata bumps it on any row touch.
        where = ":updated_at >= '{cutoff}'".format(cutoff=cutoff)
        query = urlencode({'$select': select, '$where': where, '$limit': 100000000})
        return '{}?{}'.format(cls.base_download_endpoint, query)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue

            # add primary key
            row['key'] = "{}-{}".format(row['documentid'], row['bbl'])
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def split_seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        return self.seed_with_single(delete_file=True, **kwargs)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        if settings.TESTING:
            self.seed_with_single(**kwargs)
        else:
            self.async_concurrent_seed(**kwargs)

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite. The legacy version generated FIVE correlated subqueries
        # per PA row (3 window counts + latest sale price + latest sale date),
        # each joining AcrisRealLegal → AcrisRealMaster via documentid. At
        # 873K PA rows × 5 subqueries each scanning the joined relation, this
        # was a major source of the 2026-06-14 deadlock cascade.
        #
        # New approach: two CTEs computed in single passes:
        #   - date_counts: GROUP BY l.bbl with FILTER aggregates for the 3
        #     window counts. Bounded by the outer last3years filter so the
        #     scan is small.
        #   - latest_sale: DISTINCT ON (l.bbl) ORDER BY l.bbl, m.docdate DESC
        #     to pick the row with the most recent docdate per BBL. No date
        #     window (matches legacy: latest is "ever recorded", not just
        #     within last3years).
        # Then a single UPDATE on PA joining to both via LEFT JOIN.
        from django.db import connection
        from django.utils import timezone

        last30 = dates.get_last_month_since_api_update(cls.get_dataset(), string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last3years(string=False)

        def _to_local_date(dt):
            if dt is None:
                return None
            if hasattr(dt, 'date'):
                if timezone.is_aware(dt):
                    return timezone.localtime(dt).date()
                return dt.date()
            return dt

        last30 = _to_local_date(last30)
        lastyear = _to_local_date(lastyear)
        last3years = _to_local_date(last3years)

        sale_doc_types = list(ds.AcrisRealMaster.SALE_DOC_TYPES)

        logger.info(
            'AcrisRealLegal.annotate_properties: last30=%s lastyear=%s last3years=%s sale_doc_types=%s',
            last30, lastyear, last3years, sale_doc_types,
        )
        with connection.cursor() as c:
            c.execute(
                """
                WITH date_counts AS (
                    SELECT l.bbl,
                           COUNT(*) FILTER (WHERE m.docdate >= %s) AS c30,
                           COUNT(*) FILTER (WHERE m.docdate >= %s) AS cyear,
                           COUNT(*) AS c3years
                    FROM datasets_acrisreallegal l
                    JOIN datasets_acrisrealmaster m ON m.documentid = l.documentid
                    WHERE l.bbl IS NOT NULL
                      AND m.doctype = ANY(%s)
                      AND m.docdate >= %s
                    GROUP BY l.bbl
                ),
                latest_sale AS (
                    SELECT DISTINCT ON (l.bbl)
                           l.bbl,
                           m.docdate AS latestdate,
                           m.docamount AS latestprice
                    FROM datasets_acrisreallegal l
                    JOIN datasets_acrisrealmaster m ON m.documentid = l.documentid
                    WHERE l.bbl IS NOT NULL
                      AND m.doctype = ANY(%s)
                      AND m.docdate IS NOT NULL
                    ORDER BY l.bbl, m.docdate DESC
                )
                UPDATE datasets_propertyannotation pa
                SET acrisrealmasters_last30 = COALESCE(s.c30, 0),
                    acrisrealmasters_lastyear = COALESCE(s.cyear, 0),
                    acrisrealmasters_last3years = COALESCE(s.c3years, 0),
                    latestsaleprice = s.latestprice,
                    latestsaledate = s.latestdate,
                    acrisrealmasters_lastupdated = NOW()
                FROM (
                    SELECT pa2.bbl AS bbl,
                           dc.c30, dc.cyear, dc.c3years,
                           ls.latestprice, ls.latestdate
                    FROM datasets_propertyannotation pa2
                    LEFT JOIN date_counts dc ON dc.bbl = pa2.bbl
                    LEFT JOIN latest_sale  ls ON ls.bbl = pa2.bbl
                ) s
                WHERE pa.bbl = s.bbl
                """,
                [last30, lastyear, sale_doc_types, last3years, sale_doc_types],
            )
            touched = c.rowcount
        logger.info('AcrisRealLegal.annotate_properties: %d PA rows updated', touched)


    def __str__(self):
        return self.key


@receiver(models.signals.post_save, sender=AcrisRealLegal)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            last30 = dates.get_last_month_since_api_update(
                ds.AcrisRealLegal.get_dataset(), string=False)
            lastyear = dates.get_last_year(string=False)
            last3years = dates.get_last3years(string=False)

            annotation = instance.bbl.propertyannotation
            annotation.acrisrealmasters_last30 = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last30).count(), 0)

            annotation.acrisrealmasters_lastyear = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=lastyear).count(), 0)

            annotation.acrisrealmasters_last3years = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last3years).count(), 0)

            annotation.latestsaleprice = ds.AcrisRealMaster.objects.filter(documentid__in=annotation.bbl.acrisreallegal_set.values(
                'documentid'), doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, docdate__isnull=False).latest('docdate').docamount

            annotation.save()
        except Exception as e:
            print(e)
            return
