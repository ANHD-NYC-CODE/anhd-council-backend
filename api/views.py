from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse, HttpResponseNotFound
from django.core import serializers
from django.conf import settings
from django.core.cache import cache
from api.helpers.api_helpers import queryset_by_housingtype

from datasets import models as d_models
import logging

logger = logging.getLogger('app')


@api_view(['GET'])
def councils_index(request, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        councils_json = cache.get(request.path_info)
        return JsonResponse(councils_json, safe=False)
    else:
        try:
            councils = d_models.Council.objects.all()
            councils_json = serializers.serialize('json', councils)
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, councils_json, timeout=settings.CACHE_TTL)
            return JsonResponse(councils_json, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)


@api_view(['GET'])
def council_show(request, councilnum, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        councils_json = cache.get(request.path_info)
        return JsonResponse(councils_json, safe=False)
    else:
        try:
            council = d_models.Council.objects.filter(coundist=councilnum)
            council_json = serializers.serialize('json', council)
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, council_json, timeout=settings.CACHE_TTL)
            return JsonResponse(council_json, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)


@api_view(['GET'])
def query(request, councilnum, housingtype, format=None):
    cache_key = request.path_info + request.query_params.dict().__str__()
    if cache_key in cache:
        logger.debug('Serving cache: {}'.format(cache_key))
        results_json = cache.get(cache_key)
        return JsonResponse(results_json, safe=False)
    else:
        try:
            # results = queryset_by_housingtype(housingtype)
            results = d_models.Property.objects.filter(council=councilnum)
            results_json = serializers.serialize('json', results)
            logger.debug('Caching: {}'.format(cache_key))
            cache.set(cache_key, results_json, timeout=settings.CACHE_TTL)
            return JsonResponse(results_json, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)


@api_view(['GET'])
def building_lookup(request, bbl, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        property_json = cache.get(request.path_info)
        return JsonResponse(property_json, safe=False)
    else:
        try:
            property = d_models.Property.objects.get(bbl=bbl)
            property_json = serializers.serialize('json', [property])
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, property_json, timeout=settings.CACHE_TTL)
            return JsonResponse(property_json, safe=False)
        except d_models.Property.DoesNotExist as e:
            return JsonResponse([], status=status.HTTP_404_NOT_FOUND, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
