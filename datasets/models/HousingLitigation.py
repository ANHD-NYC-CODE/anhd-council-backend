from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen
from datasets.utils.validation_filters import is_null
import logging
from django.dispatch import receiver
from datasets import models as ds
from core.tasks import async_download_and_update


logger = logging.getLogger('app')


class HousingLitigation(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-caseopendate']),
            models.Index(fields=['-caseopendate']),

        ]

    API_ID = '59kj-x8nc'
    QUERY_DATE_KEY = 'caseopendate'
    RECENT_DATE_PINNED = True
    download_endpoint = "https://data.cityofnewyork.us/api/views/59kj-x8nc/rows.csv?accessType=DOWNLOAD"

    litigationid = models.IntegerField(primary_key=True, blank=False, null=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    boro = models.SmallIntegerField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    block = models.SmallIntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    casetype = models.TextField(blank=True, null=True)
    caseopendate = models.DateField(blank=True, null=True)
    casestatus = models.TextField(blank=True, null=True)
    openjudgement = models.TextField(blank=True, null=True)
    findingofharassment = models.TextField(blank=True, null=True)
    findingdate = models.DateField(blank=True, null=True)
    penalty = models.TextField(blank=True, null=True)
    respondent = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    communitydistrict = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    nta = models.TextField(blank=True, null=True)

    slim_query_fields = ["litigationid", "bbl", "caseopendate"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['litigationid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(**kwargs)
        logger.debug('annotating properties for {}', self.__name__)
        self.annotate_properties()

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_month_offset()

    def __str__(self):
        return str(self.litigationid)


@receiver(models.signals.post_save, sender=HousingLitigation)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = sender.annotate_property_month_offset(ds.PropertyAnnotation.objects.get(bbl=instance.bbl))
            annotation.save()
        except Exception as e:
            print(e)
