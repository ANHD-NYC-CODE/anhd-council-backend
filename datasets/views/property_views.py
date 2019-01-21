from rest_framework.decorators import api_view, action
from rest_framework import renderers

from rest_framework import status

from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.core.cache import cache
from datasets.helpers.api_helpers import cache_me, properties_by_housingtype
from datasets.serializers import property_query_serializer
from datasets.models.Property import PropertyFilter
from datasets import serializers as serial


from datasets import models as ds
import logging
logger = logging.getLogger('app')


class PropertyViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Property.objects
    serializer_class = serial.PropertySerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        if 'parent_lookup_council' in kwargs:
            queryset = ds.Property.objects.council(self.kwargs['parent_lookup_council'])
        else:
            queryset = ds.Property.objects
        self.queryset = properties_by_housingtype(self.request, queryset=queryset)
        return super().list(self, request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)

    @cache_me()
    def buildings_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.PropertyBuildingsSummary
        return super().retrieve(self, request, *args, **kwargs)

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
