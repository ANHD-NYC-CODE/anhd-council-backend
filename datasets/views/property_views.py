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


from datasets import models as ds
import logging
logger = logging.getLogger('app')


class PropertyViewSet(ApplicationViewSet, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Property.objects.only('bbl', 'unitsres', 'council', 'unitstotal',
                                        'yearbuilt', 'address', 'lat', 'lng')
    serializer_class = serial.PropertySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PropertyFilter

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @cache_me()
    def buildings_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.PropertyBuildingsSummary
        return super().retrieve(request, *args, **kwargs)

#
# @api_view(['GET'])
# def query(request, councilnum, housingtype, format=None):
#     cache_key = request.path_info + request.query_params.dict().__str__()
#     if cache_key in cache:
#         logger.debug('Serving cache: {}'.format(cache_key))
#         results_json = cache.get(cache_key)
#         return Response(results_json, safe=False)
#     else:
#         try:
#             council_housing_results = properties_by_housingtype(
#                 request, queryset=ds.Property.objects.council(councilnum))
#             property_filter = PropertyFilter(request.GET, queryset=council_housing_results.all())
#             results_json = json.dump(property_query_serializer(property_filter.qs.all()))
#             logger.debug('Caching: {}'.format(cache_key))
#             cache.set(cache_key, results_json, timeout=settings.CACHE_TTL)
#             return JsonResponse(results_json, safe=False)
#         except Exception as e:
#             return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
