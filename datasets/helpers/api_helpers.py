from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from datasets import filter_helpers
from rest_framework import viewsets
from collections import OrderedDict
from copy import deepcopy
from datasets import models as ds
from functools import wraps
from django.db.models import Prefetch, Q, Count
from django.conf import settings
import logging
import json
import urllib
import datetime
import re
import datetime
logger = logging.getLogger('app')


def get_advanced_search_value(params, dataset_prefix=None, date_comparison=None):
    if not dataset_prefix:
        return None
    if 'q' in params:
        q = params['q']
        reg = r'{}([^(,| )]*)'.format(dataset_prefix)
        matches = re.findall(reg, q)

        if len(matches) > 0:
            date_match = next((x for x in matches if date_comparison in x), None)
            if date_match:

                return date_match.split('=')[1]

    return None


def get_annotation_start(params, dataset_prefix=''):

    return params.get(dataset_prefix + '__start', params.get('annotation__start', get_advanced_search_value(params, dataset_prefix, 'gte') or settings.DEFAULT_ANNOTATION_DATE))


def get_annotation_end(params, dataset_prefix=''):
    return params.get(dataset_prefix + '__end', params.get('annotation__end', get_advanced_search_value(params, dataset_prefix, 'lte') or datetime.datetime.now().strftime("%Y-%m-%d")))


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100

    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #         ('next', self.get_next_link()),
    #         ('previous', self.get_previous_link()),
    #         ('results', data)
    #     ]))


def annotated_fields_to_dict(start=None, end=None):
    #####
    # convert annotation fields to date dict
    # start = '2018-01-01'
    # {'dates': ({'__gte': 2018-01-01}, {'__lte': 2018-01-01})}
    if start:
        start = {'__gte': datetime.datetime.strptime(start, '%Y-%m-%d')}
    if end:
        end = {'__lte': datetime.datetime.strptime(end, '%Y-%m-%d')}
    return {'dates': tuple(filter(None, [start, end]))}


def prefetch_annotated_datasets(queryset, request):
    DATASETS = [ds.HPDViolation, ds.HPDComplaint, ds.DOBViolation, ds.DOBComplaint,
                ds.ECBViolation, ds.Eviction, ds.DOBIssuedPermit, ds.DOBFiledPermit]

    params = request.query_params

    annotation_dict = annotated_fields_to_dict(start=get_annotation_start(params), end=get_annotation_end(params))
    for dataset in DATASETS:
        field_path = dataset.__name__.lower() + '__' + dataset.QUERY_DATE_KEY
        date_filters = filter_helpers.value_dict_to_date_filter_dict(field_path, annotation_dict)
        # annotations get overwritten by drf filters if dataset annotation is present.

        queryset = filter_helpers.filtered_dataset_annotation(dataset.__name__.lower(), date_filters, queryset)

    queryset = queryset.prefetch_related(
        Prefetch('acrisreallegal_set', queryset=ds.AcrisRealLegal.objects.select_related('documentid')))
    return queryset


def prefetch_housingtype_sets(queryset):
    return queryset.prefetch_related(Prefetch(
        'publichousingrecord_set', queryset=ds.PublicHousingRecord.objects.only('pk', 'bbl'))).prefetch_related(Prefetch(
            'rentstabilizationrecord', queryset=ds.RentStabilizationRecord.objects.only('pk', 'ucbbl'))).prefetch_related(Prefetch(
                'coresubsidyrecord_set', queryset=ds.CoreSubsidyRecord.objects.only('pk', 'bbl'))).prefetch_related(Prefetch(
                    'subsidyj51_set', queryset=ds.SubsidyJ51.objects.only('pk', 'bbl'))).prefetch_related(Prefetch(
                        'subsidy421a_set', queryset=ds.Subsidy421a.objects.only('pk', 'bbl'))).only(*ds.Property.SHORT_SUMMARY_FIELDS)


def handle_property_summaries(self, request, *args, **kwargs):
    from datasets import serializers as serial

    if 'summary' in request.query_params and request.query_params['summary'] == 'true':
        if 'summary-type' in request.query_params and request.query_params['summary-type'].lower() == 'short':
            self.queryset = prefetch_housingtype_sets(self.queryset)

            self.serializer_class = serial.PropertyShortSummarySerializer
        elif 'summary-type' in request.query_params and request.query_params['summary-type'].lower() == 'short-annotated':
            self.queryset = prefetch_housingtype_sets(self.queryset)

            # SINGLE-QUERY METHOD CHAIN
            # self.queryset = prefetch_annotated_datasets(self.queryset, request)

            self.serializer_class = serial.PropertyShortAnnotatedSerializer
        else:
            self.queryset = self.queryset.prefetch_related('building_set').prefetch_related('hpdregistration_set').prefetch_related('taxlien_set').prefetch_related('conhrecord_set').prefetch_related(
                'publichousingrecord_set').prefetch_related('rentstabilizationrecord').prefetch_related('coresubsidyrecord_set').prefetch_related('subsidyj51_set').prefetch_related('subsidy421a_set')
            self.serializer_class = serial.PropertySummarySerializer


def add_headers(headers, **kwargs):
    return {'headers': headers, **kwargs}


class ApplicationViewSet():
    from datasets import serializers as serial

    def dispatch(self, *args, **kwargs):
        # if filename and csv in params
        if self.request.GET:
            if ('format' in self.request.GET and self.request.GET['format'] == 'csv') and 'filename' in self.request.GET:

                response = super(viewsets.ReadOnlyModelViewSet, self).dispatch(*args, **kwargs)

                response['Content-Disposition'] = "attachment; filename=%s" % (
                    self.request.GET['filename'] if 'filename' in self.request.GET else "dap-portal.csv")
                return response
            # if csv and no filename in params
            elif ('format' in self.request.GET and self.request.GET['format'] == 'csv') and 'filename' not in self.request.GET:
                response = super(viewsets.ReadOnlyModelViewSet, self).dispatch(*args, **kwargs)
                response['Content-Disposition'] = "attachment; filename=%s" % (
                    "{}-{}-dap-portal.csv".format(self.serializer_class.Meta.model.__name__, datetime.datetime.today().strftime('%Y-%m-%d')))
                return response
            else:
                response = super(viewsets.ReadOnlyModelViewSet, self).dispatch(*args, **kwargs)
                return response
        else:
            return super().dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        from datasets import serializers as serial

        self.pagination_class = StandardResultsSetPagination
        # no pagination for csv
        if ('format' in request.query_params and request.query_params['format'] == 'csv'):
            self.pagination_class = None

            if self.serializer_class.__name__ == 'AcrisRealMasterSerializer':
                self.serializer_class = serial.AcrisRealMasterCsvSerializer
            if self.serializer_class.__name__ == 'HPDRegistrationSerializer':
                self.serializer_class = serial.HPDRegistrationCsvSerializer
            if self.serializer_class.__name__ == 'HPDComplaintSerializer':
                self.serializer_class = serial.HPDComplaintCsvSerializer

        # no pagination for JSON unless 'page' is included in params
        if ('page' not in request.query_params and 'format' in request.query_params and request.query_params['format'] == 'json'):
            self.pagination_class = None

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        from datasets import serializers as serial

        # no pagination for csv
        if ('format' in request.query_params and request.query_params['format'] == 'csv'):
            self.pagination_class = None
            if self.serializer_class.__name__ == 'AcrisRealMasterSerializer':
                self.serializer_class = serial.AcrisRealMasterCsvSerializer
            if self.serializer_class.__name__ == 'HPDRegistrationSerializer':
                self.serializer_class = serial.HPDRegistrationCsvSerializer
            if self.serializer_class.__name__ == 'HPDComplaintSerializer':
                self.serializer_class = serial.HPDComplaintCsvSerializer

        # no pagination for JSON unless 'page' is included in params
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

                # cache only if response is 200
                if (response.status_code == 200):
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
