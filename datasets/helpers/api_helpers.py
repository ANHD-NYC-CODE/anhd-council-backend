from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from collections import OrderedDict
from datasets import serializers as serial
from copy import deepcopy
from datasets import models as ds
from functools import wraps
import logging
import json
import urllib
logger = logging.getLogger('app')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100

    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #         ('next', self.get_next_link()),
    #         ('previous', self.get_previous_link()),
    #         ('results', data)
    #     ]))


def add_headers(headers, **kwargs):
    return {'headers': headers, **kwargs}


class ApplicationViewSet():
    def dispatch(self, *args, **kwargs):
        if ('format' in self.request.GET and self.request.GET['format'] == 'csv') or ('format' in self.request.GET and self.request.GET['format'] == 'csv'):

            response = super(viewsets.ReadOnlyModelViewSet, self).dispatch(*args, **kwargs)

            response['Content-Disposition'] = "attachment; filename=%s" % (
                self.request.GET['filename'] if 'filename' in self.request.GET else "dap-portal.csv")
            return response
        else:
            response = super(viewsets.ReadOnlyModelViewSet, self).dispatch(*args, **kwargs)
            return response

    def list(self, request, *args, **kwargs):

        self.pagination_class = StandardResultsSetPagination
        if ('format' in request.query_params and request.query_params['format'] == 'csv') or ('format' in request.query_params and request.query_params['format'] == 'csv'):
            self.pagination_class = None

            if self.serializer_class.__name__ == 'AcrisRealMasterSerializer':
                self.serializer_class = serial.AcrisRealMasterCsvSerializer
            if self.serializer_class.__name__ == 'HPDRegistrationSerializer':
                self.serializer_class = serial.HPDRegistrationCsvSerializer
            if self.serializer_class.__name__ == 'HPDComplaintSerializer':
                self.serializer_class = serial.HPDComplaintCsvSerializer

        if ('page' not in request.query_params and 'format' in request.query_params and request.query_params['format'] == 'json'):
            self.pagination_class = None

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if ('format' in request.query_params and request.query_params['format'] == 'csv') or ('format' in request.query_params and request.query_params['format'] == 'csv'):
            self.pagination_class = None

            if self.serializer_class.__name__ == 'AcrisRealMasterSerializer':
                self.serializer_class = serial.AcrisRealMasterCsvSerializer
            if self.serializer_class.__name__ == 'HPDRegistrationSerializer':
                self.serializer_class = serial.HPDRegistrationCsvSerializer
            if self.serializer_class.__name__ == 'HPDComplaintSerializer':
                self.serializer_class = serial.HPDComplaintCsvSerializer

        if ('page' not in request.query_params and 'format' in request.query_params and request.query_params['format'] == 'json'):
            self.pagination_class = None

        return super().retrieve(request, *args, **kwargs)


def cache_me(relative_key_path=True, get_queryset=False):
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):

            params = deepcopy(original_args[1].query_params)
            params.pop('format', None)
            params.pop('filename', None)
            cache_key = original_args[1].path + '?' + urllib.parse.urlencode(params)

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
