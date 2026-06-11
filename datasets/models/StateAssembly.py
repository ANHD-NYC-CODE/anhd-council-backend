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
# https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyad/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson
# Paste into a .geojson file, upload file through admin, update.
#
# On a successful upload, seed_or_update_self auto-nulls every
# Property.stateassembly and dispatches `async_add_state_geo_links`. That task
# uses prepared-geometry point-in-polygon (see PR #147) to recompute all
# Property.stateassembly assignments against the new shapes — ~15-30 min on
# prod hardware for ~873K properties. Pre-PR-#147 this loop took 4-5 days,
# which is why prior versions of this file ran the recompute only manually.

class StateAssembly(BaseDatasetModel, models.Model):
    id = models.IntegerField(primary_key=True, blank=False, null=False)
    data = JSONField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path, update=None):
        return from_geojson(file_path, pk="AssemDist")

    @classmethod
    def seed_or_update_self(cls, **kwargs):
        result = cls.seed_with_upsert(**kwargs)
        # New polygons uploaded — null Property.stateassembly so the geo loop
        # recomputes from scratch against the new shapes. Without this, the
        # `__isnull=True` filter in add_state_geographies would skip every row.
        from datasets import models as ds
        from core.tasks import async_add_state_geo_links
        nulled = ds.Property.objects.exclude(stateassembly__isnull=True).update(stateassembly=None)
        logger.info('StateAssembly upload: nulled %d Property.stateassembly, dispatching recompute', nulled)
        async_add_state_geo_links.delay()
        return result

    def __str__(self):
        return str(self.id)
