from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from datasets.helpers.api_helpers import cache_me

from datasets import serializers as serial
from datasets import models as ds


class BuildingViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Building.objects
    serializer_class = serial.BuildingSerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        # if 'parent_lookup_property' in kwargs:
        #     self.queryset = self.queryset.filter(bbl=self.kwargs['parent_lookup_property'])
        return super().list(self, request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)
