from rest_framework.decorators import api_view
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
        property = cache.get(request.path_info)
    else:
        logger.debug('Caching: {}'.format(request.path_info))
        property = serializers.serialize('json', [d_models.Property.objects.filter(bbl=bbl)[0]])
        cache.set(request.path_info, property, timeout=settings.CACHE_TTL)
    return JsonResponse(property, safe=False)
