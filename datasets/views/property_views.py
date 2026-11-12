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
from core import models as c_models
from core.custom_search_concurrency import custom_search_concurrency_slot
from core.custom_search_policy import (
    is_blocked_borough_unfiltered_custom_search,
    is_blocked_citywide_custom_search,
    is_any_custom_search_json_list,
)
from core.throttling import is_internal_cache_request
import logging
logger = logging.getLogger('app')

CITYWIDE_CUSTOM_SEARCH_BLOCKED_DETAIL = (
    'Citywide custom search is not available. '
    'Choose a borough, district, or use the District Dashboard for all of NYC.'
)
BOROUGH_CUSTOM_SEARCH_BLOCKED_DETAIL = (
    'Borough custom search requires a specific housing type or at least one dataset filter.'
)
CUSTOM_SEARCH_BUSY_DETAIL = (
    'Too many custom searches are running. Please wait a moment and try again.'
)


class PropertyViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(
        api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Property.objects
    serializer_class = serial.PropertySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PropertyFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not self.request:
            return context
        if 'summary' in self.request.query_params and self.request.query_params['summary'] == 'true':
            if 'summary-type' in self.request.query_params and (self.request.query_params['summary-type'].lower() == 'short-annotated' or self.request.query_params['summary-type'].lower() == 'custom-search'):
                # calculate dynamic annotation fields here.
                datasets = c_models.Dataset.objects.all()
                context['datasets'] = list(datasets)
                context['fields'] = build_annotated_fields(
                    self.request, list(datasets))
        return context

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        # Policy + concurrency protect public gunicorn workers. Internal callers
        # (whoisit: saved-search notifications run in Celery via the test
        # Client, pre-warm, async jobs that already validated at start) are exempt.
        internal = is_internal_cache_request(request)

        if not internal and is_blocked_citywide_custom_search(request):
            return Response(
                {'detail': CITYWIDE_CUSTOM_SEARCH_BLOCKED_DETAIL},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not internal and is_blocked_borough_unfiltered_custom_search(request):
            return Response(
                {'detail': BOROUGH_CUSTOM_SEARCH_BLOCKED_DETAIL},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def _execute_list():
            if 'q' in request.query_params:
                self.filterset_class = AdvancedPropertyFilter

            handle_property_summaries(self, request, *args, **kwargs)

            return super(PropertyViewSet, self).list(request, *args, **kwargs)

        run_concurrency_limit = is_any_custom_search_json_list(request) and not internal
        if not run_concurrency_limit:
            return _execute_list()

        with custom_search_concurrency_slot() as acquired:
            if not acquired:
                return Response(
                    {'detail': CUSTOM_SEARCH_BUSY_DETAIL},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            return _execute_list()

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
