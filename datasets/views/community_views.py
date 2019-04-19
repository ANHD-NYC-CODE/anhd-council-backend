from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datasets.helpers.api_helpers import cache_me, ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class CommunityViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    community_housing:
    Returns the counts of each housing type in the community district.

    ### Query Params:

    #### unitsres=`number`
      - adjusts the small homes definition to correspond to less than or equal to the specified number. Blank defaults to lte 6

    #### program=`name`
      - filters the rent regulated results to only count properties with the specified program name. Defaults to all core data + j-51 + 421a properties
    """
    EXCLUDED_COMMUNITY_PKS = ('164', '226', '227', '228', '355', '356', '480', '481', '482', '483', '484', '595')
    queryset = ds.Community.objects.exclude(pk__in=EXCLUDED_COMMUNITY_PKS).all().order_by('pk')
    serializer_class = serial.CommunitySerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def community_housing(self, request, *args, **kwargs):
        self.serializer_class = serial.CommunityHousingTypeSummarySerializer
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def council_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.CommunitySummarySerializer
        return super().retrieve(request, *args, **kwargs)
