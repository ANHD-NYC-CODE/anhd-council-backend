from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import JsonResponse, HttpResponseNotFound
from django.core import serializers
from django.conf import settings
from django.core.cache import cache
from datasets.helpers.api_helpers import queryset_by_housingtype
from datasets.serializers import property_query_serializer, property_lookup_serializer
from datasets.models.Property import PropertyFilter
from datasets import serializers as serial


from datasets import models as ds
import logging
import json
logger = logging.getLogger('app')


def council_list(request):
    if request.method == 'GET':
        if request.path_info in cache:
            logger.debug('Serving cache: {}'.format(request.path_info))
            return JsonResponse(cache.get(request.path_info), safe=False)
        else:
            try:
                councils = ds.Council.objects.all()
            except ds.Council.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            try:
                serializer = serial.CouncilSerializer(councils, many=True)
                logger.debug('Caching: {}'.format(request.path_info))
                cache.set(request.path_info, serializer.data, timeout=settings.CACHE_TTL)
                return JsonResponse(serializer.data, safe=False)
            except Exception as e:
                return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
    else:
        return HttpResponse(400)


def council_detail(request, pk):
    if request.method == 'GET':
        if request.path_info in cache:
            logger.debug('Serving cache: {}'.format(request.path_info))
            return JsonResponse(cache.get(request.path_info), safe=False)
        else:
            try:
                council = ds.Council.objects.get(pk=pk)
            except ds.Council.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            try:
                serializer = serial.CouncilDetailSerializer(council)
                logger.debug('Caching: {}'.format(request.path_info))
                cache.set(request.path_info, serializer.data, timeout=settings.CACHE_TTL)
                return JsonResponse(serializer.data, safe=False)
            except Exception as e:
                return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
    else:
        return HttpResponse(400)


@api_view(['GET'])
def query(request, councilnum, housingtype, format=None):
    cache_key = request.path_info + request.query_params.dict().__str__()
    if cache_key in cache:
        logger.debug('Serving cache: {}'.format(cache_key))
        results_json = cache.get(cache_key)
        return JsonResponse(results_json, safe=False)
    else:
        try:
            council_housing_results = queryset_by_housingtype(ds.Property.objects.council(councilnum), housingtype)
            property_filter = PropertyFilter(request.GET, queryset=council_housing_results.all())
            results_json = json.dump(property_query_serializer(property_filter.qs.all()))
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, results_json, timeout=settings.CACHE_TTL)
            return JsonResponse(results_json, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)


@api_view(['GET'])
def property_lookup(request, bbl, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        property_json = cache.get(request.path_info)
        return JsonResponse(property_json, safe=False)
    else:
        try:
            property = ds.Property.objects.get(bbl=bbl)
            property_json = property_lookup_serializer(property)
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, property_json, timeout=settings.CACHE_TTL)
            return JsonResponse(property_json, safe=False)
        except ds.Property.DoesNotExist as e:
            return JsonResponse([], status=status.HTTP_404_NOT_FOUND, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
