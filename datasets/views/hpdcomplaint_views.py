from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet

from django.db.models import Q

from datasets import serializers as serial
from datasets import models as ds


class HPDComplaintViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(
        api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.HPDComplaint.objects.all().order_by('pk')
    serializer_class = serial.HPDComplaintSerializer

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
