from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds


class StateAssemblyViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ds.StateAssembly.objects.all().order_by('pk')
    serializer_class = serial.StateAssemblySerializer

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
