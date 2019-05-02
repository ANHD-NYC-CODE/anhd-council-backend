from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import datetime
import logging
logger = logging.getLogger('app')
from datasets import models as ds
from core.tasks import async_download_and_update
from core.tasks import async_download_and_update


from django.dispatch import receiver


# Update process: Manual
# Update strategy: Overwrite
# Add version (year)
# Download: https://data.cityofnewyork.us/api/views/bzxi-2tsw/rows.csv?accessType=DOWNLOAD


class CONHRecord(BaseDatasetModel, models.Model):
    API_ID = 'bzxi-2tsw'
    download_endpoint = "https://data.cityofnewyork.us/api/views/bzxi-2tsw/rows.csv?accessType=DOWNLOAD"

    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    buildingid = models.TextField(blank=True, null=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    ntaneighborhoodtabulationarea = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    slim_query_fields = ["id", 'bbl']

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)
        self.annotate_properties()

    @classmethod
    def annotate_properties(self):
        for record in self.objects.all():
            try:
                annotation = record.bbl.propertyannotation
                annotation.conhrecord = True
                annotation.save()
            except Exception as e:
                print(e)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=CONHRecord)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = ds.PropertyAnnotation.objects.get(bbl=instance.bbl)
            annotation.conhrecord = True
            annotation.save()
        except Exception as e:
            print(e)
