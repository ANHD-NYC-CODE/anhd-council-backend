from django.db import models
from django.db.models import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson


# Update process: Manual
# Update strategy: Upsert
#
# Copy data in a file called councils.geojson from:
# City Council Districts > Clipped to Shoreline > GeoJson
# https://www1.nyc.gov/site/planning/data-maps/open-data/districts-download-metadata.page
# Paste into a .geojson file, upload file through admin, update

class Council(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="CounDist")

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.id)
