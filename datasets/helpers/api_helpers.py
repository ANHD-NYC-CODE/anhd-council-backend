from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict

from datasets import models as ds
from functools import wraps
import logging

logger = logging.getLogger('app')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class ApplicationViewSet():
    def list(self, request, *args, **kwargs):
        self.pagination_class = StandardResultsSetPagination
        if ('format' in kwargs and kwargs['format'] == 'csv') or ('format' in request.query_params and request.query_params['format'] == 'csv'):
            self.pagination_class = None
        if ('format' in kwargs and kwargs['format'] == 'json'):
            self.pagination_class = None
        return super().list(request, *args, **kwargs)


def cache_me(relative_key_path=True, get_queryset=False):
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):
            cache_key = original_args[1].build_absolute_uri()
            # TODO - figure out a way to inject cached data into renderer / response for browsable API pagination
            # or skip caching on the django RF browsable api templates since they don't work ideally - loses pagination and filters
            # if original_args[1].accepted_renderer.format == 'api':
            #     return function(*original_args, **original_kwargs)
            if cache_key in cache:
                # cached response will not display pagination buttons in browsable API view
                # but otherwise preserves the pagination data
                logger.debug('Serving cache: {}'.format(cache_key))
                return original_args[0].finalize_response(original_args[1], Response(cache.get(cache_key)))
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
