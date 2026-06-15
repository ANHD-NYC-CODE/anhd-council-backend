from django.db import models
from django.dispatch import receiver
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils import dates
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware

from datetime import datetime
from core.utils.database import execute
from datasets import models as ds

import logging
logger = logging.getLogger('app')

# Supertable of PSPreforeclosure and PSForeclosure
# Update Instructions:
# 1. Login to Property Shark on 1st of the month
# 2. Download Foreclosures AND Preforeclosures from last month
# 3. upload PSPreforeclosures first, PSForeclosures second
# 4. No need to create an update for this model - all seeding + annotation done inside PSPreforeclosure and PSForeclosure


class Foreclosure(BaseDatasetModel, models.Model):
    QUERY_DATE_KEY = 'date_added'
    RECENT_DATE_PINNED = True
    REQUIRES_AUTHENTICATION = True
    # Tells dataset to get the last update timestamp from this model
    UPDATE_SOURCE = "PSPreForeclosure"

    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-date_added']),
            models.Index(fields=['-date_added']),
        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    index = models.TextField(blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    document_type = models.TextField(blank=True, null=True)
    lien_type = models.TextField(blank=True, null=True)  # lispendens blank
    # fileddate in LisPenden and date_added for PropertyShark
    date_added = models.DateField(blank=True, null=True)
    creditor = models.TextField(blank=True, null=True)
    debtor = models.TextField(blank=True, null=True)
    mortgage_date = models.TextField(blank=True, null=True)
    mortgage_amount = models.TextField(blank=True, null=True)
    # only from PropertySharkForeclosure
    auction = models.DateField(blank=True, null=True)
    foreign_key = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)  # PDC or PropertyShark

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite of an O(rows × correlated subqueries) UPDATE. Same shape
        # as BaseDatasetModel._annotate_all_properties_grouped — single GROUP
        # BY aggregation limited to the last3years window, then UPDATE all PA
        # rows via LEFT JOIN. Replaces the legacy Subquery+Coalesce pattern
        # that deadlocked under concurrent runs on 2026-06-14.
        from django.db import connection
        from django.utils import timezone

        last30 = dates.get_last_month_since_api_update(cls.get_dataset(), string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last3years(string=False)

        # date_added is a postgres `date`. Match Django ORM coercion: convert
        # UTC datetime → local-TZ → date so the SQL boundary matches the
        # legacy Coalesce(subquery_gte_datetime, 0) behavior exactly.
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

        logger.info(
            'Foreclosure.annotate_properties: last30=%s lastyear=%s last3years=%s',
            last30, lastyear, last3years,
        )
        with connection.cursor() as c:
            # Skip-unchanged-rows: only touch PA rows whose value could
            # possibly differ. A row is skippable when (a) no source records
            # in last3years (LEFT JOIN gives NULL) AND (b) all three current
            # counts are already 0. Foreclosure is sparse (~57K source rows
            # on local, ~similar on prod), so most BBLs get skipped — big
            # write reduction. Semantically identical output.
            c.execute(
                """
                UPDATE datasets_propertyannotation pa
                SET foreclosures_last30 = COALESCE(s.c30, 0),
                    foreclosures_lastyear = COALESCE(s.cyear, 0),
                    foreclosures_last3years = COALESCE(s.c3years, 0),
                    foreclosures_lastupdated = NOW()
                FROM (
                    SELECT pa2.bbl AS bbl, agg.c30, agg.cyear, agg.c3years
                    FROM datasets_propertyannotation pa2
                    LEFT JOIN (
                        SELECT bbl,
                               COUNT(*) FILTER (WHERE date_added >= %s) AS c30,
                               COUNT(*) FILTER (WHERE date_added >= %s) AS cyear,
                               COUNT(*) AS c3years
                        FROM datasets_foreclosure
                        WHERE bbl IS NOT NULL AND date_added >= %s
                        GROUP BY bbl
                    ) agg ON agg.bbl = pa2.bbl
                    WHERE agg.bbl IS NOT NULL
                       OR pa2.foreclosures_last30 > 0
                       OR pa2.foreclosures_lastyear > 0
                       OR pa2.foreclosures_last3years > 0
                ) s
                WHERE pa.bbl = s.bbl
                """,
                [last30, lastyear, last3years],
            )
            touched = c.rowcount
        logger.info('Foreclosure.annotate_properties: %d PA rows updated', touched)

    def __str__(self):
        return str(self.key)

    @classmethod
    def seed_lispendens(self):
        def get_lien_type(related_comments):
            for rc in related_comments:
                if 'mortgage' in rc.datecomments.lower():
                    return 'Mortgage'
                elif 'tax lien' in rc.datecomments.lower():
                    return 'Tax Lien'

        lispendens = ds.LisPenden.objects.filter(
            type='foreclosure', bbl__isnull=False).distinct('index')
        foreclosures = []

        for lispenden in lispendens:
            related_comments = ds.LisPendenComment.objects.prefetch_related(
                'key').filter(key=lispenden.key)
            try:
                foreclosures.append(
                    Foreclosure(
                        key="{}-{}".format(lispenden.index, lispenden.bbl_id),
                        bbl=lispenden.bbl,
                        index=lispenden.index,
                        document_type="Lis Pendens",
                        lien_type=get_lien_type(related_comments),
                        date_added=lispenden.fileddate,
                        creditor=lispenden.cr,
                        debtor=lispenden.debtor,
                        foreign_key=lispenden.key,
                        source='Public Data Corporation'
                    )
                )
            except Exception as e:
                print(e)

        ds.Foreclosure.objects.bulk_create(foreclosures)


@receiver(models.signals.post_save, sender=Foreclosure)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            last30 = dates.get_last_month(string=False)
            lastyear = dates.get_last_year(string=False)
            last3years = dates.get_last3years(string=False)

            annotation = instance.bbl.propertyannotation
            annotation.foreclosures_last30 = Coalesce(
                annotation.bbl.foreclosure_set.filter(date_added__gte=last30).count(), 0)

            annotation.foreclosures_lastyear = Coalesce(
                annotation.bbl.foreclosure_set.filter(date_added__gte=lastyear).count(), 0)

            annotation.foreclosures_last3years = Coalesce(
                annotation.bbl.foreclosure_set.filter(date_added__gte=last3years).count(), 0)

            annotation.save()
        except Exception as e:
            print(e)
