from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_xlsx_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging
import datetime
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Combine all borough files downloaded from DOF into single xlsx file under a worksheet named "Web File"
# https://www1.nyc.gov/site/finance/taxes/property-lien-sales.page
# upload file through admin, then update

class TaxLien(BaseDatasetModel, models.Model):
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
    waterdebtonly = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_xlsx_file_to_gen(file_path, 'Web File', update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.id)
