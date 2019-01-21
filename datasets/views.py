from rest_framework.decorators import api_view
from rest_framework.views import APIView

from rest_framework import status, mixins, generics

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_extensions.mixins import NestedViewSetMixin

from django.http import JsonResponse, HttpResponseNotFound, Http404
from django.core import serializers
from django.conf import settings
from django.core.cache import cache
from datasets.helpers.api_helpers import properties_by_housingtype
from datasets.serializers import property_query_serializer, property_lookup_serializer
from datasets.models.Property import PropertyFilter
from datasets import serializers as serial

from functools import wraps


from datasets import models as ds
import logging
import json
logger = logging.getLogger('app')


def cache_me(relative_key_path=True, get_queryset=False):
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):
            cache_key = original_args[1].build_absolute_uri()

            if cache_key in cache:
                logger.debug('Serving cache: {}'.format(cache_key))
                return Response(cache.get(cache_key))
            else:
                response = function(*original_args, **original_kwargs)

                logger.debug('Caching: {}'.format(cache_key))
                cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
                return response

        return cached_view
    return cache_decorator


class CouncilViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )
    queryset = ds.Council.objects
    serializer_class = serial.CouncilSerializer

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)

    @cache_me()
    def housingtype_summary(self, request, *args, **kwargs):
        self.serializer_class = serial.CouncilHousingTypeSummarySerializer
        return super().retrieve(self, request, *args, **kwargs)

    @cache_me()
    def properties(self, request, *args, **kwargs):
        self.queryset = properties_by_housingtype(self.request, queryset=ds.Property.objects.council(self.kwargs['pk']))
        self.serializer_class = serial.PropertySerializer
        return super().list(self, request, *args, **kwargs)


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


@api_view(['GET'])
def query(request, councilnum, housingtype, format=None):
    cache_key = request.path_info + request.query_params.dict().__str__()
    if cache_key in cache:
        logger.debug('Serving cache: {}'.format(cache_key))
        results_json = cache.get(cache_key)
        return Response(results_json, safe=False)
    else:
        try:
            council_housing_results = properties_by_housingtype(
                request, queryset=ds.Property.objects.council(councilnum))
            property_filter = PropertyFilter(request.GET, queryset=council_housing_results.all())
            results_json = json.dump(property_query_serializer(property_filter.qs.all()))
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, results_json, timeout=settings.CACHE_TTL)
            return JsonResponse(results_json, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
