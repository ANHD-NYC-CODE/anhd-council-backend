from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datasets.helpers.api_helpers import cache_me, ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class CouncilViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    council_housing:
    Returns the counts of each housing type in the council district.

    ### Query Params:

    #### sh_units=`number`
      - adjusts the small homes definition to correspond to less than or equal to the specified number. Blank defaults to lte 6

    #### program=`name`
      - filters the rent regulated results to only count properties with the specified program name. Defaults to all core data + j-51 + 421a properties
    """
    queryset = ds.Council.objects.all().order_by('pk')
    serializer_class = serial.CouncilSerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def council_housing(self, request, *args, **kwargs):
        self.serializer_class = serial.CouncilHousingTypeSummarySerializer
        return super().retrieve(request, *args, **kwargs)
