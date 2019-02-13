from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Overwrite
#
# Download file from:
# https://github.com/JustFixNYC/nycha-scraper
# upload file through admin then update


class PublicHousingRecord(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    development = models.TextField(blank=True, null=True)
    managedby = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    facility = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.id)
