from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from django.conf import settings
from django.dispatch import receiver
from datasets import models as ds
from django.db.models import Count, OuterRef, Q
import os
import csv
import uuid
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
logger = logging.getLogger('app')


class AcrisRealLegal(BaseDatasetModel, models.Model):
    download_endpoint = 'https://data.cityofnewyork.us/api/views/8h5j-fqxa/rows.csv?accessType=DOWNLOAD'
    QUERY_DATE_KEY = 'documentid__docdate'

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
    goodthroughdate = models.DateTimeField(blank=True, null=True)

    slim_query_fields = ["bbl", "documentid"]

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue

            row['key'] = "{}-{}".format(row['documentid'], row['bbl'])  # add primary key
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
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_with_single(delete_file=True, **kwargs)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        if settings.TESTING:
            self.seed_with_single(**kwargs)
            self.annotate_properties()
        else:
            self.async_concurrent_seed(**kwargs)

        # self.annotate_properties() # run this in an async scheduled task

    @classmethod
    def annotate_properties(self):
        count = 0
        records = []
        logger.debug('annotating properties for:'.format(self.__name__))
        for annotation in ds.PropertyAnnotation.objects.all():
            try:
                last30 = datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)
                lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
                last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

                annotation.acrisrealmasters_last30 = annotation.bbl.acrisreallegal_set.filter(
                    documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last30).count()

                annotation.acrisrealmasters_lastyear = annotation.bbl.acrisreallegal_set.filter(
                    documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=lastyear).count()

                annotation.acrisrealmasters_last3years = annotation.bbl.acrisreallegal_set.filter(
                    documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last3years).count()

                annotation.latestsaleprice = ds.AcrisRealMaster.objects.filter(documentid__in=annotation.bbl.acrisreallegal_set.values(
                    'documentid'), doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES).latest('docdate').docamount
                records.append(annotation)
                count = count + 1
                if count % settings.BATCH_SIZE == 0:
                    logger.debug('preloaded: '.format(count))

            except Exception as e:
                continue
        logger.debug('beginning bulk_update for:'.format(self.__name__))
        ds.PropertyAnnotation.objects.bulk_update(records, ['latestsaleprice', 'acrisrealmasters_last30',
                                                            'acrisrealmasters_lastyear',
                                                            'acrisrealmasters_last3years'], batch_size=settings.BATCH_SIZE)

    def __str__(self):
        return self.key


@receiver(models.signals.post_save, sender=AcrisRealLegal)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            last30 = datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)
            lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
            last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

            annotation = ds.PropertyAnnotation.objects.get(bbl=instance.bbl)
            annotation.acrisrealmasters_last30 = annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last30).count()

            annotation.acrisrealmasters_lastyear = annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=lastyear).count()

            annotation.acrisrealmasters_last3years = annotation.bbl.acrisreallegal_set.filter(
                documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, documentid__docdate__gte=last3years).count()

            annotation.latestsaleprice = ds.AcrisRealMaster.objects.filter(documentid__in=annotation.bbl.acrisreallegal_set.values(
                'documentid'), doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES).latest('docdate').docamount

            annotation.save()
        except Exception as e:
            print(e)
            return
