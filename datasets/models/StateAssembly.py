from django.db import models
from django.contrib.postgres.fields import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson


# Update process: Manual
# Update strategy: Upsert
#
# Copy data from:
# https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyad/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson
# Paste into a .geojson file, upload file through admin, update

class StateAssembly(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="AssemDist")

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.id)
