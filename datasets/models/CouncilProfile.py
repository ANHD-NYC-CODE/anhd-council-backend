from django.db import models
from django.db.models import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson


# Update process: Manual
# Update strategy: Upsert

class CouncilProfile(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    council_member_name = models.TextField(blank=True, null=True)
    neighborhood_list = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.id)
