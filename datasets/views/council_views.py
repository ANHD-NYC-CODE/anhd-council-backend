from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datasets.helpers.api_helpers import cache_me, ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class CouncilViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ds.Council.objects.all().order_by('pk')
    serializer_class = serial.CouncilSerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def council_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.CouncilHousingTypeSummarySerializer
        return super().retrieve(request, *args, **kwargs)
