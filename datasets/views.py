from rest_framework.decorators import api_view
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as rf_csv


from django.http import JsonResponse, HttpResponseNotFound, Http404
from django.core import serializers
from django.conf import settings
from django.core.cache import cache
from datasets.helpers.api_helpers import properties_by_housingtype
from datasets.serializers import property_query_serializer, property_lookup_serializer
from datasets.models.Property import PropertyFilter
from datasets import serializers as serial


from datasets import models as ds
import logging
import json
logger = logging.getLogger('app')


class CouncilList(APIView):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )

    def get(self, request, format=None):
        cache_key = request.path_info
        if cache_key in cache:
            logger.debug('Serving cache: {}'.format(cache_key))
            return Response(cache.get(cache_key))
        else:
            councils = ds.Council.objects.all()
            serializer = serial.CouncilSerializer(councils, many=True)
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
            return Response(serializer.data)


class CouncilDetail(APIView):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )

    def get_object(self, pk):
        try:
            return ds.Council.objects.get(pk=pk)
        except ds.Council.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        cache_key = request.path_info
        if cache_key in cache:
            logger.debug('Serving cache: {}'.format(cache_key))
            return Response(cache.get(cache_key))
        else:
            council = self.get_object(pk)
            serializer = serial.CouncilDetailSerializer(council)
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
            return Response(serializer.data)


class CouncilPropertyList(APIView):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )

    def get_object(self, pk):
        try:
            return ds.Council.objects.get(pk=pk)
        except ds.Council.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        cache_key = request.build_absolute_uri()
        if cache_key in cache:
            logger.debug('Serving cache: {}'.format(cache_key))
            return Response(cache.get(cache_key))
        else:
            council = self.get_object(pk)
            properties = properties_by_housingtype(request, queryset=ds.Property.objects.filter(council=council))
            serializer = serial.PropertySerializer(properties, many=True)
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
            return Response(serializer.data)


class PropertyDetail(APIView):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (rf_csv.CSVRenderer, )

    def get_object(self, pk):
        try:
            return ds.Property.objects.get(pk=pk)
        except ds.Property.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if request.path_info in cache:
            logger.debug('Serving cache: {}'.format(request.path_info))
            return Response(cache.get(request.path_info))
        else:
            property = self.get_object(pk)
            serializer = serial.PropertySerializer(property)
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, serializer.data, timeout=settings.CACHE_TTL)
            return Response(serializer.data)


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
