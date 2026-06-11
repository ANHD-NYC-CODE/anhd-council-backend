import logging

from django.db import models
from django.db.models import JSONField
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_geojson

logger = logging.getLogger('app')

# Update process: Manual upload (when NYC redistricts, ~every 10 years)
# Update strategy: Upsert + auto-recompute Property assignments
#
# Copy data from:
# http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyss/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson
# Paste into a .geojson file, upload file through admin, update.
#
# Second Step: After updating the dataset, make sure to update or create a new
# map on https://studio.mapbox.com/ by uploading the shapefile dataset/zipfiles
# and then update the api link on the front end app "/src/LeafletMap/index.js"
# for the zipcode api with the new mapbox map.
#
# Make sure to clear cache after. If you see overlapping layers or old dataset
# data still even after updating, please make sure your browser cache is
# cleared or test in a private browser.
#
# AUTO-RECOMPUTE (new in PR #148):
# On a successful upload, seed_or_update_self auto-nulls every
# Property.statesenate and dispatches `async_add_state_geo_links`. That task
# uses prepared-geometry point-in-polygon (see PR #147) to recompute all
# Property.statesenate assignments against the new shapes — ~15-30 min on prod
# hardware for ~873K properties.
#
# Pre-PR-#147 the recompute loop took 4-5 days (re-parsed each polygon for each
# property, ~80M shape() calls in pure Python) — which is why the historical
# workflow was to null fields manually + start the recompute days in advance.
# That history note is preserved here so future devs understand why the auto-
# recompute hook was off by default for so long.

class StateSenate(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="StSenDist")

    @classmethod
    def seed_or_update_self(cls, **kwargs):
        result = cls.seed_with_upsert(**kwargs)
        # New polygons uploaded — null Property.statesenate so the geo loop
        # recomputes from scratch against the new shapes. Without this, the
        # `__isnull=True` filter in add_state_geographies would skip every row.
        from datasets import models as ds
        from core.tasks import async_add_state_geo_links
        nulled = ds.Property.objects.exclude(statesenate__isnull=True).update(statesenate=None)
        logger.info('StateSenate upload: nulled %d Property.statesenate, dispatching recompute', nulled)
        async_add_state_geo_links.delay()
        return result

    def __str__(self):
        return str(self.id)
