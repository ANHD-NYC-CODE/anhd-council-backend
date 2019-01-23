from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from datasets.helpers.api_helpers import cache_me, ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class HPDContactViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.HPDContact.objects.all().order_by('pk')
    serializer_class = serial.HPDContactSerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
