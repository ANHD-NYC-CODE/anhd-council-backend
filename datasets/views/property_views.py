from rest_framework.decorators import api_view, action
from rest_framework import renderers
from django.db.models import Prefetch

from rest_framework import status

from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.core.cache import cache
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import build_annotated_fields, handle_property_summaries, properties_by_housingtype, ApplicationViewSet
from datasets.serializers import property_query_serializer
from datasets.filters import PropertyFilter, AdvancedPropertyFilter
from datasets import serializers as serial
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated
import json

from datasets import models as ds
import logging
logger = logging.getLogger('app')


class PropertyViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Property.objects
    serializer_class = serial.PropertySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PropertyFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not self.request:
            return context
        if 'summary' in self.request.query_params and self.request.query_params['summary'] == 'true':
            if 'summary-type' in self.request.query_params and self.request.query_params['summary-type'].lower() == 'short-annotated':
                # calculate dynamic annotation fields here.
                context['fields'] = build_annotated_fields(self.request)
        return context

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        if 'q' in request.query_params:
            self.filterset_class = AdvancedPropertyFilter

        handle_property_summaries(self, request, *args, **kwargs)

        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        handle_property_summaries(self, request, *args, **kwargs)

        return super().retrieve(request, *args, **kwargs)

    @cache_request_path()
    def buildings_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.PropertyBuildingsSummary
        return super().retrieve(request, *args, **kwargs)

    def property_bbls(self, request, *args, **kwargs):
        bbls = json.loads(request.body.decode('utf-8'))

        handle_property_summaries(self, request, *args, **kwargs)

        self.queryset = self.queryset.filter(bbl__in=bbls)
        return super().list(request, *args, **kwargs)
