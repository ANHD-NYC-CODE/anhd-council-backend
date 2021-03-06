from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
from django.db.models import OuterRef, Subquery
from datasets import models as ds
from django.dispatch import receiver
from core.tasks import async_download_and_update


import logging
logger = logging.getLogger('app')


class HPDComplaint(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-receiveddate']),
            models.Index(fields=['-receiveddate']),

        ]
    API_ID = 'uwyv-629c'
    download_endpoint = "https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD"
    QUERY_DATE_KEY = 'receiveddate'
    RECENT_DATE_PINNED = True

    complaintid = models.IntegerField(
        primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    boroughid = models.IntegerField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    communityboard = models.IntegerField(blank=True, null=True)
    receiveddate = models.DateField(blank=True, null=True)
    statusid = models.IntegerField(blank=True, null=True)
    status = models.TextField(db_index=True, blank=True, null=True)
    statusdate = models.DateField(blank=True, null=True)

    slim_query_fields = ["complaintid", "bbl", "receiveddate"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['complaintid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('StatusDate') and is_older_than(row[headers.index('StatusDate')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def add_bins_from_buildingid(self):
        logger.debug(" * Adding BINs through building for HPD Complaints.")
        bin = ds.HPDBuildingRecord.objects.filter(
            buildingid=OuterRef('buildingid')).values_list('bin')[:1]
        self.objects.prefetch_related(
            'buildingid').all().update(bin=Subquery(bin))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(callback=self.add_bins_from_buildingid, **kwargs)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_month_offset()

    def __str__(self):
        return str(self.complaintid)


@receiver(models.signals.post_save, sender=HPDComplaint)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = sender.annotate_property_month_offset(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
