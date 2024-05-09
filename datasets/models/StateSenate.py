from django.db import models
from django.db.models import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson


# Update process: Manual
# Update strategy: Upsert
#
# Copy data from:
# http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyss/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson
# Paste into a .geojson file, upload file through admin, update.

# Second Step: After updating the dataset, make sure to update or create a new map on https://studio.mapbox.com/ by uploading the shapefile dataset/zipfiles and then update the api link on the front end app "/src/LeafletMap/index.js" for the zipcode api with the new mapbox map.

# Make sure to clear cache after. If you see overlapping layers or old dataset data still even after updating, please make sure your browser cache is cleared or test in a private browser.

# As a note, a property will NOT currently update its state senate, assembly, etc unless it doesn't currently have one ('null') or is a new property. I assume it was coded this way because it takes 2-3 seconds to calculate each state senate, etc, based on its geoshape location and long/latitude. To update in 2022, I null'd each  state senate entry as I updated the properties to ensure they updated. The entire process took about 4-5 days to recalculate each properties new District based on it's map location.

class StateSenate(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="StSenDist")

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.id)
