from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds
from datasets.filters import AddressRecordFilter

from django_filters.rest_framework import DjangoFilterBackend


class AddressRecordViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ds.AddressRecord.objects.all().order_by('pk')
    serializer_class = serial.AddressRecordSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AddressRecordFilter

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
