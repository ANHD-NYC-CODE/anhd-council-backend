from rest_framework import serializers
from datasets import models as ds


def council_housing_type_dict(councilnum):
    council_buildings = ds.Property.objects.council(councilnum)
    return {
        "buildings_count": council_buildings.count(),
        "rent_stabilized_count": council_buildings.rentstab().count(),
        "rent_regulated_count": council_buildings.rentreg().count(),
        "small_homes_count": council_buildings.smallhome().count(),
        "market_rate_count": council_buildings.marketrate().count(),
    }
