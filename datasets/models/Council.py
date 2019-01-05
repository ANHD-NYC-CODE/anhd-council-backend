from django.db import models
from django.contrib.postgres.fields import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_council_geojson


class Council(BaseDatasetModel, models.Model):
    coundist = models.IntegerField(primary_key=True, blank=False, null=False)
    shapearea = models.DecimalField(decimal_places=10, max_digits=24, blank=True, null=True)
    shapelength = models.DecimalField(decimal_places=10, max_digits=24, blank=True, null=True)
    geometry = JSONField(blank=False, null=False)
    council_member_name = models.TextField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path):
        return from_council_geojson(file_path)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_overwrite(**kwargs)

    def __str__(self):
        return str(self.coundist)
