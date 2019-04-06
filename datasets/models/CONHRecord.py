from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
# Add version (year)
# Download: https://data.cityofnewyork.us/api/views/bzxi-2tsw/rows.csv?accessType=DOWNLOAD


class COHNRecord(BaseDatasetModel, models.Model):

    download_endpoint = "https://data.cityofnewyork.us/api/views/bzxi-2tsw/rows.csv?accessType=DOWNLOAD"

    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    buildingid = models.TextField(blank=True, null=True)
    bin = models.TextField(blank=True, null=True)

    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    nta = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    slim_query_fields = ["id", 'bbl']

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.id)
