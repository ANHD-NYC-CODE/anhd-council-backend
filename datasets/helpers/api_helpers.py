from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from datasets import filter_helpers
from rest_framework import viewsets
from collections import OrderedDict
from datasets import models as ds
from django.db.models import Subquery, OuterRef, Count, Prefetch, Q, IntegerField
from django.conf import settings
import logging
import json
from datetime import datetime, timezone
from datasets.utils import dates
import re
logger = logging.getLogger('app')


def get_advanced_search_value(params, dataset_prefix=None, date_field='', date_comparison='gte'):
    if not dataset_prefix:
        return None
    if 'q' in params:
        q = params['q']
        reg = r'{}([^(,| )]*)'.format(dataset_prefix)
        matches = re.findall(reg, q)

        if len(matches) > 0:
            date_match = next((x for x in matches if "{}__{}".format(date_field, date_comparison) in x), None)
            if date_match:
                return date_match.split('=')[1]

    return None


def get_recent_dataset_start(start, dataset):
    if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:
        return dates.get_last_month(string=True)

    return dates.get_last_30(string=True)


def get_annotation_start(params, dataset=None, date_field=''):
    dataset_prefix = dataset.__name__.lower() + 's'

    start = settings.DEFAULT_ANNOTATION_DATE
    if dataset_prefix + '__start' in params:
        start = params.get(dataset_prefix + '__start')
    elif 'annotation__start' in params:
        if params['annotation__start'] == 'recent':
            start = get_recent_dataset_start(params.get('annotation__start'), dataset)
        else:
            start = params['annotation__start']
    elif 'q' in params:
        start = get_advanced_search_value(params, dataset_prefix, date_field, 'gte')

    if start:
        return start
    else:
        return settings.DEFAULT_ANNOTATION_DATE


def get_annotation_end(params, dataset_prefix='', date_field=''):
    return params.get(dataset_prefix + '__end', params.get('annotation__end', get_advanced_search_value(params, dataset_prefix, date_field, 'lte') or datetime.now().strftime("%Y-%m-%d")))


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100

    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #         ('next', self.get_next_link()),
    #         ('previous', self.get_previous_link()),
    #         ('results', data)
    #     ]))


def annotated_fields_to_dict(start=None, end=None, dataset=None):
    #####
    # convert annotation fields to date dict
    # start = '2018-01-01'
    # {'dates': ({'__gte': 2018-01-01}, {'__lte': 2018-01-01})}

    if start == 'recent':
        start = get_recent_dataset_start(start, dataset)
    if start:
        start = {'__gte': datetime.strptime(start, '%Y-%m-%d')}
    if end:
        end = {'__lte': datetime.strptime(end, '%Y-%m-%d')}
    return {'dates': tuple(filter(None, [start, end]))}


def prefetch_annotated_datasets(queryset, request):
    DATASETS = [ds.HPDViolation, ds.HPDComplaint, ds.DOBViolation, ds.DOBComplaint,
                ds.ECBViolation, ds.DOBIssuedPermit, ds.DOBFiledPermit, ds.DOBIssuedPermit, ds.Eviction, ds.LisPenden, ds.HousingLitigation, ds.AcrisRealMaster]

    params = request.query_params

    for dataset in DATASETS:
        if dataset == ds.AcrisRealMaster:
            dataset_prefix = 'acrisreallegal'
            annotation_dict = annotated_fields_to_dict(dataset=dataset, start=get_annotation_start(
                params, dataset, dataset.QUERY_DATE_KEY), end=get_annotation_end(params, '', dataset.QUERY_DATE_KEY))

            field_path = 'documentid__' + dataset.QUERY_DATE_KEY
            date_filters = filter_helpers.value_dict_to_date_filter_dict(field_path, annotation_dict)
            count_subquery = Subquery(ds.AcrisRealLegal.objects.filter(bbl=OuterRef('bbl'), documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES, **date_filters).values(
                'bbl').annotate(count=Count('bbl')).values('count'), output_field=IntegerField())
            queryset = queryset.prefetch_related(dataset_prefix + '_set').annotate(**
                                                                                   {'acrisrealmasters': count_subquery})
        elif dataset == ds.LisPenden:
            dataset_prefix = dataset.__name__.lower()
            annotation_dict = annotated_fields_to_dict(dataset=dataset, start=get_annotation_start(
                params, dataset, dataset.QUERY_DATE_KEY), end=get_annotation_end(params, '', dataset.QUERY_DATE_KEY))

            field_path = dataset.QUERY_DATE_KEY
            date_filters = filter_helpers.value_dict_to_date_filter_dict(field_path, annotation_dict)
            count_subquery = Subquery(dataset.objects.filter(bbl=OuterRef('bbl'), type='foreclosure', **date_filters).values(
                'bbl').annotate(count=Count('bbl')).values('count'), output_field=IntegerField())
            queryset = queryset.prefetch_related(dataset_prefix + '_set').annotate(**
                                                                                   {dataset_prefix + 's': count_subquery})

        else:
            dataset_prefix = dataset.__name__.lower()
            annotation_dict = annotated_fields_to_dict(dataset=dataset, start=get_annotation_start(
                params, dataset, dataset.QUERY_DATE_KEY), end=get_annotation_end(params, '', dataset.QUERY_DATE_KEY))

            field_path = dataset.QUERY_DATE_KEY
            date_filters = filter_helpers.value_dict_to_date_filter_dict(field_path, annotation_dict)
            count_subquery = Subquery(dataset.objects.filter(bbl=OuterRef('bbl'), **date_filters).values(
                'bbl').annotate(count=Count('bbl')).values('count'), output_field=IntegerField())
            queryset = queryset.prefetch_related(dataset_prefix + '_set').annotate(**
                                                                                   {dataset_prefix + 's': count_subquery})

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
            self.queryset = self.queryset.select_related('propertyannotation')
            self.serializer_class = serial.PropertyShortSummarySerializer
        elif 'summary-type' in request.query_params and request.query_params['summary-type'].lower() == 'short-annotated':
            self.queryset = prefetch_housingtype_sets(self.queryset)
            self.queryset = self.queryset.select_related('propertyannotation')
            # SINGLE-QUERY METHOD CHAIN
            self.queryset = prefetch_annotated_datasets(self.queryset, request)

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
                    "{}-{}-dap-portal.csv".format(self.serializer_class.Meta.model.__name__, datetime.today().strftime('%Y-%m-%d')))
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
