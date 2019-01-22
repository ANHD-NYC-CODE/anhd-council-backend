from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from datasets import models as ds
from functools import wraps
import logging

logger = logging.getLogger('app')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100


class ApplicationViewSet():
    def list(self, request, *args, **kwargs):
        if 'format' not in kwargs or kwargs['format'] != 'csv':
            self.pagination_class = StandardResultsSetPagination
        return super().list(self, request, *args, **kwargs)


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


def properties_by_housingtype(request, queryset=None):
    if not queryset:
        queryset = ds.Property.objects

    if 'housingtype' in request.query_params:
        switcher = {
            "rentstabilized": queryset.rentstab(),
            "rentregulated": queryset.rentreg(),
            "smallhomes": queryset.smallhome(),
            "marketrate": queryset.marketrate()
        }

        return switcher.get(request.query_params['housingtype'], queryset)
    else:
        return queryset
