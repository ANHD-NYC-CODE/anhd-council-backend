from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
from django.core.cache import cache


from datasets import models as d_models
import logging

logger = logging.getLogger('app')


@api_view(['GET'])
def councils_index(request, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        councils = cache.get(request.path_info)
    else:
        logger.debug('Caching: {}'.format(request.path_info))
        councils = serializers.serialize('json', d_models.Council.objects.all())
        cache.set(request.path_info, councils, timeout=settings.CACHE_TTL)
    return JsonResponse(councils, safe=False)


@api_view(['GET'])
def building_lookup(request, bbl, format=None):
    if request.path_info in cache:
        logger.debug('Serving cache: {}'.format(request.path_info))
        property_json = cache.get(request.path_info)
        return JsonResponse(property_json, safe=False)
    else:
        try:
            property = d_models.Property.objects.get(bb1l=bbl)
            property_json = serializers.serialize('json', [property])
            logger.debug('Caching: {}'.format(request.path_info))
            cache.set(request.path_info, property_json, timeout=settings.CACHE_TTL)
            return JsonResponse(property_json, safe=False)
        except d_models.Property.DoesNotExist as e:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND, safe=False)
        except Exception as e:
            return JsonResponse(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
