from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet
from django.http import HttpResponseForbidden


from datasets import serializers as serial
from datasets import models as ds

from rest_framework.permissions import IsAuthenticated


class OCAHousingCourtViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.OCAHousingCourt.objects.all().order_by('pk')
    serializer_class = serial.OCAHousingCourtSerializer
    permission_classes = (IsAuthenticated,)

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return response
        except Exception as e:
            return HttpResponseForbidden()


    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return response
