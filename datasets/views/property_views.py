from rest_framework.decorators import api_view, action
from rest_framework import renderers

from rest_framework import status

from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.core.cache import cache
from datasets.helpers.api_helpers import cache_me, properties_by_housingtype, ApplicationViewSet
from datasets.serializers import property_query_serializer
from datasets.filters import PropertyFilter
from datasets import serializers as serial
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated


from datasets import models as ds
import logging
logger = logging.getLogger('app')


class PropertyViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Property.objects.only('bbl', 'unitsres', 'council', 'unitstotal', 'unitsrentstabilized',
                                        'yearbuilt', 'bldgclass',
                                        'numbldgs', 'address', 'lat', 'lng')
    serializer_class = serial.PropertySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PropertyFilter
    # permission_classes = (IsAuthenticated,)

    @cache_me()
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated and 'q' in request.query_params and 'lispenden' in request.query_params['q']:
            return Response({'detail': 'Please login to view lispenden results'}, status=401)
        return super().list(request, *args, **kwargs)
        # try:
        # except Exception as e:
        #     return Response(e, status=500)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def property_summary(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            self.serializer_class = serial.AuthenticatedPropertySummarySerializer
        else:
            self.serializer_class = serial.PropertySummarySerializer
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def buildings_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.PropertyBuildingsSummary
        return super().retrieve(request, *args, **kwargs)
