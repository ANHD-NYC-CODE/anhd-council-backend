from django.dispatch import receiver
from datasets import models as ds
from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
from core.tasks import async_download_and_update
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Combine all borough xlsx files downloaded from DOF into single csv file
# Add a "year" column and enter the year for every row in the CSV
# https://www1.nyc.gov/site/finance/taxes/property-lien-sales.page
# upload file through admin, then update

class TaxLien(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/9rz4-mjek/rows.csv?accessType=DOWNLOAD"
    API_ID = '9rz4-mjek'

    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    taxclasscode = models.TextField(blank=True, null=True)
    buildingclass = models.TextField(blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    waterdebtonly = models.BooleanField(blank=True, null=True)
    year = models.SmallIntegerField(db_index=True, blank=True, null=True)
    month = models.TextField(blank=True, null=True)
    cycle = models.TextField(blank=True, null=True)

    slim_query_fields = ["id", 'bbl', 'year']

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if not is_null(row['waterdebtonly']):
                waterdebtonly = row['waterdebtonly'] == 'YES'
                row['waterdebtonly'] = waterdebtonly
            if not is_null(row['month']):
                month = row['month'].split('/')[0]
                year = row['month'].split('/')[1]
                row['month'] = month
                row['year'] = year
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(self):
        for record in self.objects.all():
            try:
                annotation = record.bbl.propertyannotation
                annotation.taxlien = True
                annotation.save()
            except Exception as e:
                print(e)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=TaxLien)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            annotation.taxlien = True
            annotation.save()
        except Exception as e:
            print(e)
