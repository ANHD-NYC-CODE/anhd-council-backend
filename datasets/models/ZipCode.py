from django.db import models
from django.contrib.postgres.fields import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson


# Update process: Manual
# Update strategy: Upsert
#
# 
# First Step: When importing new geojson dataset, Please ensure 'postalCode' is column/id name, and not zipcode for coding purposes. 
# Second Step: After updating the dataset, make sure to update or create a new map on https://studio.mapbox.com/ by uploading the shapefile dataset/zipfiles and then update the api link on the front end app "/src/LeafletMap/index.js" for the zipcode api with the new mapbox map.
# Make sure to clear cache after. If you see overlapping layers or old dataset data still even after updating, please make sure your browser cache is cleared or test in a private browser.

class ZipCode(BaseDatasetModel, models.Model):
    id = models.CharField(primary_key=True, max_length=5, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="postalCode")

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.id)
