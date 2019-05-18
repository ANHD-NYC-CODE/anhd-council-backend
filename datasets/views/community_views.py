from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class CommunityViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    EXCLUDED_COMMUNITY_PKS = ('164', '226', '227', '228', '355', '356', '480', '481', '482', '483', '484', '595')
    queryset = ds.Community.objects.exclude(pk__in=EXCLUDED_COMMUNITY_PKS).all().order_by('pk')
    serializer_class = serial.CommunitySerializer

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @cache_request_path()
    def community_housing(self, request, *args, **kwargs):
        self.serializer_class = serial.CommunityHousingTypeSummarySerializer
        return super().retrieve(request, *args, **kwargs)

    @cache_request_path()
    def council_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.CommunitySummarySerializer
        return super().retrieve(request, *args, **kwargs)
