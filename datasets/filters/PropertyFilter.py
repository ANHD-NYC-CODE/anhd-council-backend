from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField, Case, When, Value, Exists, OuterRef, FilteredRelation, Prefetch
from django.db.models.functions import Cast
import django_filters
from datasets.filter_helpers import filtered_dataset_annotation, value_dict_to_date_filter_dict, CommaSeparatedConditionFilter, TotalWithDateFilter, RSLostPercentWithDateFilter, PercentWithDateField, AdvancedQueryFilter
from datasets.utils import advanced_filter as af
import operator
from functools import reduce
from django.db.models import Q

from django.conf import settings

import logging

logger = logging.getLogger('app')


def housingtype_filter(self, queryset, name, value):
    switcher = {
        "rs": queryset.rentstab(),
        "rr": queryset.rentreg(),
        "sh": queryset.smallhome(),
        "mr": queryset.marketrate(),
        "ph": queryset.publichousing(),
        "all": queryset.residential()
    }
    return switcher.get(value, queryset.none())


def rsunits_filter(self, queryset, name, values):
    return queryset.rs_annotate().annotate(rslostpercent=Case(When(**{values['start_year']: 0}, then=0), When(**{values['end_year']: 0}, then=1), default=ExpressionWrapper(1 - Cast(F(values['end_year']), FloatField()) / Cast(F(values['start_year']), FloatField()), output_field=FloatField()), output_field=FloatField())).filter(**values['percent_query'])

# Subsidy Program Names


def programnames_filter(self, queryset, name, value):
    qs = []

    if value['exact']:
        return queryset.filter(**{"{}__icontains".format(name): value['exact']}).distinct('bbl')
    if value['icontains']:
        return queryset.filter(**{"{}__icontains".format(name): value['icontains']}).distinct('bbl')
    if value['any']:
        qs.append(reduce(operator.or_, (Q(
            **{"{}__icontains".format(name): item}) for item in value['any'])))
    if value['all']:
        qs.append(reduce(operator.and_, (Q(
            **{"{}__icontains".format(name): item}) for item in value['all'])))

    combined_q = reduce(operator.and_, (q for q in qs))

    return queryset.filter(combined_q).distinct('bbl')


def has_date_filter(query_params):
    for key in query_params.dict().keys():
        if 'start' in key or 'end' in key:
            return True
    return False


class PropertyFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        return super(PropertyFilter, self).__init__(*args, **kwargs)

    @property
    def qs(self):
        return super(PropertyFilter, self).qs

    council = django_filters.NumberFilter(method='filter_council_exact')
    cd = django_filters.NumberFilter(method='filter_community_exact')
    zipcode = django_filters.NumberFilter(method='filter_zipcode_exact')
    stateassembly = django_filters.NumberFilter(
        method='filter_stateassembly_exact')
    statesenate = django_filters.NumberFilter(
        method='filter_statesenate_exact')

    housingtype = filters.CharFilter(method='filter_housingtype')
    bbls = CommaSeparatedConditionFilter(method="filter_bbls")
    hpdcomplaints__exact = django_filters.NumberFilter(
        method='filter_hpdcomplaints_exact')
    hpdcomplaints__gt = django_filters.NumberFilter(
        method='filter_hpdcomplaints_gt')
    hpdcomplaints__gte = django_filters.NumberFilter(
        method='filter_hpdcomplaints_gte')
    hpdcomplaints__lt = django_filters.NumberFilter(
        method='filter_hpdcomplaints_lt')
    hpdcomplaints__lte = django_filters.NumberFilter(
        method='filter_hpdcomplaints_lte')
    hpdcomplaints = TotalWithDateFilter(
        method="filter_hpdcomplaints_total_and_dates")

    hpdviolations__exact = django_filters.NumberFilter(
        method='filter_hpdviolations_exact')
    hpdviolations__gt = django_filters.NumberFilter(
        method='filter_hpdviolations_gt')
    hpdviolations__gte = django_filters.NumberFilter(
        method='filter_hpdviolations_gte')
    hpdviolations__lt = django_filters.NumberFilter(
        method='filter_hpdviolations_lt')
    hpdviolations__lte = django_filters.NumberFilter(
        method='filter_hpdviolations_lte')
    hpdviolations = TotalWithDateFilter(
        method="filter_hpdviolations_total_and_dates")

    dobcomplaints__exact = django_filters.NumberFilter(
        method='filter_dobcomplaints_exact')
    dobcomplaints__gt = django_filters.NumberFilter(
        method='filter_dobcomplaints_gt')
    dobcomplaints__gte = django_filters.NumberFilter(
        method='filter_dobcomplaints_gte')
    dobcomplaints__lt = django_filters.NumberFilter(
        method='filter_dobcomplaints_lt')
    dobcomplaints__lte = django_filters.NumberFilter(
        method='filter_dobcomplaints_lte')
    dobcomplaints = TotalWithDateFilter(
        method="filter_dobcomplaints_total_and_dates")

    dobviolations__exact = django_filters.NumberFilter(
        method='filter_dobviolations_exact')
    dobviolations__gt = django_filters.NumberFilter(
        method='filter_dobviolations_gt')
    dobviolations__gte = django_filters.NumberFilter(
        method='filter_dobviolations_gte')
    dobviolations__lt = django_filters.NumberFilter(
        method='filter_dobviolations_lt')
    dobviolations__lte = django_filters.NumberFilter(
        method='filter_dobviolations_lte')
    dobviolations = TotalWithDateFilter(
        method="filter_dobviolations_total_and_dates")

    ecbviolations__exact = django_filters.NumberFilter(
        method='filter_ecbviolations_exact')
    ecbviolations__gt = django_filters.NumberFilter(
        method='filter_ecbviolations_gt')
    ecbviolations__gte = django_filters.NumberFilter(
        method='filter_ecbviolations_gte')
    ecbviolations__lt = django_filters.NumberFilter(
        method='filter_ecbviolations_lt')
    ecbviolations__lte = django_filters.NumberFilter(
        method='filter_ecbviolations_lte')
    ecbviolations = TotalWithDateFilter(
        method="filter_ecbviolations_total_and_dates")

    rsunitslost = RSLostPercentWithDateFilter(
        method="filter_stabilizedunitslost_percent_and_dates")

    acrisrealmasteramounts = TotalWithDateFilter(
        method="filter_acrisrealmasteramounts_total_and_dates")
    acrisrealmasters = TotalWithDateFilter(
        method="filter_acrisrealmasters_total_and_dates")

    dobfiledpermits = TotalWithDateFilter(
        method="filter_dobfiledpermits_total_and_dates")
    dobissuedpermits = TotalWithDateFilter(
        method="filter_dobissuedpermits_total_and_dates")
    evictions = TotalWithDateFilter(method="filter_eviction_total_and_dates")

    taxlien = django_filters.NumberFilter(
        field_name='taxlien__year', lookup_expr='exact')
    taxlien__lt = django_filters.NumberFilter(
        field_name='taxlien__year', lookup_expr='lt')
    taxlien__lte = django_filters.NumberFilter(
        field_name='taxlien__year', lookup_expr='lte')
    taxlien__gt = django_filters.NumberFilter(
        field_name='taxlien__year', lookup_expr='gt')
    taxlien__gte = django_filters.NumberFilter(
        field_name='taxlien__year', lookup_expr='gte')

    coresubsidyrecord__enddate__lte = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='lte')
    coresubsidyrecord__enddate__lt = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='lt')
    coresubsidyrecord__enddate = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='exact')
    coresubsidyrecord__enddate__gte = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='gte')
    coresubsidyrecord__enddate__gt = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='gt')
    subsidyprograms__programname = CommaSeparatedConditionFilter(
        method="filter_programnames")

    def filter_council_exact(self, queryset, name, value):
        return queryset.council(value)

    def filter_community_exact(self, queryset, name, value):
        return queryset.community(value)

    def filter_zipcode_exact(self, queryset, name, value):
        return queryset.zipcode(value)

    def filter_stateassembly_exact(self, queryset, name, value):
        return queryset.stateassembly(value)

    def filter_statesenate_exact(self, queryset, name, value):
        return queryset.statesenate(value)

    def parse_totaldate_field_values(self, date_prefix, totals_prefix, values):
        date_filters = value_dict_to_date_filter_dict(date_prefix, values)
        total_filters = {}

        for item in values['totals']:
            for k, v in item.items():
                if v is not None:
                    total_filters[totals_prefix + k] = v

        return (date_filters, total_filters)

    def filter_housingtype(self, queryset, name, value):
        return housingtype_filter(self, queryset, name, value)

    def filter_bbls(self, queryset, name, value):
        bbls = value['exact'].split(',')
        return queryset.filter(bbl__in=bbls)

    # Rent stabilized units lost

    def filter_stabilizedunitslost_percent_and_dates(self, queryset, name, values):
        return rsunits_filter(self, queryset, name, values)

    # Subsidy Program Names

    def filter_programnames(self, queryset, name, value):
        return programnames_filter(self, queryset, 'propertyannotation__subsidyprograms', value)

    def filter_acrisrealmasteramounts_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'documentid__docdate', 'documentid__docamount', values)
        docid_values = ds.AcrisRealMaster.construct_sales_query(
            'acrisreallegal__documentid').only('documentid')
        documenttype_queryset = ds.AcrisRealLegal.objects.filter(bbl__in=queryset.values('bbl'),
                                                                 documentid__in=docid_values).only('bbl', 'documentid')

        filtered_acris = documenttype_queryset.filter(
            **date_filters).filter(**total_filters).only('bbl').filter(bbl=OuterRef('bbl'))

        queryset = queryset.annotate(has_filtered_acris=Exists(
            filtered_acris)).filter(has_filtered_acris=True)

        return queryset

        date_filters, total_filters = self.parse_totaldate_field_values(
            'acrisreallegal__' + ds.AcrisRealLegal.QUERY_DATE_KEY, 'acrisrealmasters', values)
        queryset = queryset.annotate(acrisrealmasters=Count(
            'acrisreallegal__documentid', distinct=True))

        return queryset.filter(acrisreallegal__bbl__in=queryset.values('bbl'), **date_filters, **total_filters).distinct()

    def filter_acrisrealmasters_total_and_dates(self, queryset, name, values):

        # queryset = filtered_dataset_annotation('acrisreallegal__documentid', date_filters, queryset)

        # date_filters, total_filters = self.parse_totaldate_field_values('documentid__docdate', 'documentid', values)
        # docid_values = ds.AcrisRealMaster.construct_sales_query('acrisreallegal__documentid').only('documentid')
        # documenttype_queryset = ds.AcrisRealLegal.objects.filter(bbl__in=queryset.values('bbl'),
        #                                                          documentid__in=docid_values).only('bbl', 'documentid')
        #
        #
        # filtered_acris = documenttype_queryset.filter(
        #     **date_filters).filter(**total_filters).only('bbl').filter(bbl=OuterRef('bbl'))
        #
        # queryset = queryset.annotate(has_filtered_acris=Exists(filtered_acris))
        # return queryset.filter(has_filtered_acris=True)
        date_filters, total_filters = self.parse_totaldate_field_values(
            'acrisreallegal__' + ds.AcrisRealLegal.QUERY_DATE_KEY, 'acrisrealmasters', values)
        queryset = queryset.annotate(acrisrealmasters=Count('acrisreallegal__documentid', filter=Q(ds.AcrisRealMaster.sales_q(
            relation_path='acrisreallegal__documentid'), **date_filters), distinct=True))

        return queryset.filter(**date_filters, **total_filters).distinct()

    def filter_dobissuedpermits_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobissuedpermit__' + ds.DOBIssuedPermit.QUERY_DATE_KEY, 'dobissuedpermits', values)

        queryset = filtered_dataset_annotation(
            'dobissuedpermit', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_dobfiledpermits_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobfiledpermit__' + ds.DOBFiledPermit.QUERY_DATE_KEY, 'dobfiledpermits', values)

        queryset = filtered_dataset_annotation(
            'dobfiledpermit', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_eviction_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'eviction__' + ds.Eviction.QUERY_DATE_KEY, 'evictions', values)
        queryset = filtered_dataset_annotation(
            'eviction', date_filters, queryset)

        return queryset.filter(**total_filters)

    # HPD Complaints

    def filter_hpdcomplaints_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'hpdcomplaint__' + ds.HPDComplaint.QUERY_DATE_KEY, 'hpdcomplaints', values)
        queryset = filtered_dataset_annotation(
            'hpdcomplaint', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_hpdcomplaints_exact(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints=value)

    def filter_hpdcomplaints_gt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gt=value)

    def filter_hpdcomplaints_gte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gte=value).distinct()

    def filter_hpdcomplaints_lt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lt=value)

    def filter_hpdcomplaints_lte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lte=value)

    # HPD Violations
    def filter_hpdviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'hpdviolation__' + ds.HPDViolation.QUERY_DATE_KEY, 'hpdviolations', values)

        queryset = filtered_dataset_annotation(
            'hpdviolation', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_hpdviolations_exact(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    def filter_hpdviolations_gt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gt=value)

    def filter_hpdviolations_gte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset

        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gte=value)

    def filter_hpdviolations_lt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lt=value)

    def filter_hpdviolations_lte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lte=value)

    # DOB Complaints
    def filter_dobcomplaints_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobcomplaint__' + ds.DOBComplaint.QUERY_DATE_KEY, 'dobcomplaints', values)
        queryset = filtered_dataset_annotation(
            'dobcomplaint', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_dobcomplaints_exact(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints=value)

    def filter_dobcomplaints_gt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__gt=value)

    def filter_dobcomplaints_gte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__gte=value)

    def filter_dobcomplaints_lt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__lt=value)

    def filter_dobcomplaints_lte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__lte=value)

    # DOBViolations
    def filter_dobviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobviolation__' + ds.DOBViolation.QUERY_DATE_KEY, 'dobviolations', values)
        queryset = filtered_dataset_annotation(
            'dobviolation', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_dobviolations_exact(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations=value)

    def filter_dobviolations_gt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gt=value)

    def filter_dobviolations_gte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gte=value)

    def filter_dobviolations_lt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lt=value)

    def filter_dobviolations_lte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lte=value)

    # ECBViolations
    def filter_ecbviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'ecbviolation__' + ds.ECBViolation.QUERY_DATE_KEY, 'ecbviolations', values)
        queryset = filtered_dataset_annotation(
            'ecbviolation', date_filters, queryset)

        return queryset.filter(**total_filters)

    def filter_ecbviolations_exact(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations=value)

    def filter_ecbviolations_gt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gt=value)

    def filter_ecbviolations_gte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gte=value)

    def filter_ecbviolations_lt(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lt=value)

    def filter_ecbviolations_lte(self, queryset, name, value):
        if has_date_filter(self.request.query_params):
            return queryset
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lte=value)

    class Meta:
        model = ds.Property
        fields = {
            'borough': ['exact'],
            'address': ['exact', 'icontains'],
            'yearbuilt': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'unitsres': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'unitstotal': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'bldgclass': ['exact'],
            'numbldgs': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'numfloors': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'propertyannotation__legalclassb': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'propertyannotation__managementprogram': ['exact', 'icontains'],
            'rentstabilizationrecord__uc2007': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2008': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2009': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2010': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2011': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2012': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2013': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2014': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2015': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2017': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2018': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2019': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2020': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2021': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2022': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2023': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rentstabilizationrecord__uc2024': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
