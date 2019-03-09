from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField, Case, When, Value, Exists, OuterRef, FilteredRelation, Prefetch
from django.db.models.functions import Cast
import django_filters
from django import forms
from copy import deepcopy
from datasets.filter_helpers import CommaSeparatedConditionFilter, TotalWithDateFilter, RSLostPercentWithDateFilter, PercentWithDateField, AdvancedQueryFilter
from datasets.utils import advanced_filter as af
import operator
from functools import reduce
from django.db.models import Q

from collections import OrderedDict
from django.conf import settings
from psycopg2.extras import DateRange


def housingtype_filter(self, queryset, name, value):
    switcher = {
        "rs": queryset.rentstab(),
        "rr": queryset.rentreg(),
        "sh": queryset.smallhome(),
        "mr": queryset.marketrate(),
        "ph": queryset.publichousing()
    }
    return switcher.get(value, queryset.none())


def rsunits_filter(self, queryset, name, values):
    return queryset.rs_annotate().annotate(rslostpercent=Case(When(**{values['start_year']: 0}, then=0), When(**{values['end_year']: 0}, then=1), default=ExpressionWrapper(1 - Cast(F(values['end_year']), FloatField()) / Cast(F(values['start_year']), FloatField()), output_field=FloatField()), output_field=FloatField())).filter(**values['percent_query'])


class PropertyFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        return super(PropertyFilter, self).__init__(*args, **kwargs)

    @property
    def qs(self):
        return super(PropertyFilter, self).qs

    council = django_filters.NumberFilter(method='filter_council_exact')
    cd = django_filters.NumberFilter(method='filter_community_exact')

    housingtype = filters.CharFilter(method='filter_housingtype')

    hpdcomplaints__exact = django_filters.NumberFilter(method='filter_hpdcomplaints_exact')
    hpdcomplaints__gt = django_filters.NumberFilter(method='filter_hpdcomplaints_gt')
    hpdcomplaints__gte = django_filters.NumberFilter(method='filter_hpdcomplaints_gte')
    hpdcomplaints__lt = django_filters.NumberFilter(method='filter_hpdcomplaints_lt')
    hpdcomplaints__lte = django_filters.NumberFilter(method='filter_hpdcomplaints_lte')
    hpdcomplaints = TotalWithDateFilter(method="filter_hpdcomplaints_total_and_dates")

    hpdviolations__exact = django_filters.NumberFilter(method='filter_hpdviolations_exact')
    hpdviolations__gt = django_filters.NumberFilter(method='filter_hpdviolations_gt')
    hpdviolations__gte = django_filters.NumberFilter(method='filter_hpdviolations_gte')
    hpdviolations__lt = django_filters.NumberFilter(method='filter_hpdviolations_lt')
    hpdviolations__lte = django_filters.NumberFilter(method='filter_hpdviolations_lte')
    hpdviolations = TotalWithDateFilter(method="filter_hpdviolations_total_and_dates")

    dobcomplaints__exact = django_filters.NumberFilter(method='filter_dobcomplaints_exact')
    dobcomplaints__gt = django_filters.NumberFilter(method='filter_dobcomplaints_gt')
    dobcomplaints__gte = django_filters.NumberFilter(method='filter_dobcomplaints_gte')
    dobcomplaints__lt = django_filters.NumberFilter(method='filter_dobcomplaints_lt')
    dobcomplaints__lte = django_filters.NumberFilter(method='filter_dobcomplaints_lte')
    dobcomplaints = TotalWithDateFilter(method="filter_dobcomplaints_total_and_dates")

    dobviolations__exact = django_filters.NumberFilter(method='filter_dobviolations_exact')
    dobviolations__gt = django_filters.NumberFilter(method='filter_dobviolations_gt')
    dobviolations__gte = django_filters.NumberFilter(method='filter_dobviolations_gte')
    dobviolations__lt = django_filters.NumberFilter(method='filter_dobviolations_lt')
    dobviolations__lte = django_filters.NumberFilter(method='filter_dobviolations_lte')
    dobviolations = TotalWithDateFilter(method="filter_dobviolations_total_and_dates")

    ecbviolations__exact = django_filters.NumberFilter(method='filter_ecbviolations_exact')
    ecbviolations__gt = django_filters.NumberFilter(method='filter_ecbviolations_gt')
    ecbviolations__gte = django_filters.NumberFilter(method='filter_ecbviolations_gte')
    ecbviolations__lt = django_filters.NumberFilter(method='filter_ecbviolations_lt')
    ecbviolations__lte = django_filters.NumberFilter(method='filter_ecbviolations_lte')
    ecbviolations = TotalWithDateFilter(method="filter_ecbviolations_total_and_dates")

    rsunitslost = RSLostPercentWithDateFilter(method="filter_stabilizedunitslost_percent_and_dates")

    acrisrealmasteramounts = TotalWithDateFilter(method="filter_acrisrealmasteramounts_total_and_dates")
    acrisrealmastersales = TotalWithDateFilter(method="filter_acrisrealmastersales_total_and_dates")

    dobissuedpermits = TotalWithDateFilter(method="filter_dobpermitissued_total_and_dates")
    evictions = TotalWithDateFilter(method="filter_eviction_total_and_dates")

    taxlien = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='exact')
    taxlien__lt = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='lt')
    taxlien__lte = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='lte')
    taxlien__gt = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='gt')
    taxlien__gte = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='gte')

    coresubsidyrecord__enddate__lte = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='date__lte')
    coresubsidyrecord__enddate__lt = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='date__lt')
    coresubsidyrecord__enddate = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='date__exact')
    coresubsidyrecord__enddate__gte = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='date__gte')
    coresubsidyrecord__enddate__gt = django_filters.DateFilter(
        field_name='coresubsidyrecord__enddate', lookup_expr='date__gt')
    coresubsidyrecord__programname = CommaSeparatedConditionFilter(method="filter_programnames")

    def filter_council_exact(self, queryset, name, value):
        return queryset.council(value)

    def filter_community_exact(self, queryset, name, value):
        return queryset.community(value)

    def parse_totaldate_field_values(self, date_prefix, totals_prefix, values):
        date_filters = {}
        total_filters = {}

        for item in values['dates']:
            for k, v in item.items():
                if v is not None:
                    date_filters[date_prefix + k] = v
        for item in values['totals']:
            for k, v in item.items():
                if v is not None:
                    total_filters[totals_prefix + k] = v

        return (date_filters, total_filters)

    def filter_housingtype(self, queryset, name, value):
        return housingtype_filter(self, queryset, name, value)

    # Rent stabilized units lost

    def filter_stabilizedunitslost_percent_and_dates(self, queryset, name, values):
        return rsunits_filter(self, queryset, name, values)

    def filter_acrisrealmasteramounts_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'documentid__docdate', 'documentid__docamount', values)
        documenttype_queryset = ds.AcrisRealLegal.objects.filter(documentid__in=ds.AcrisRealMaster.construct_sales_query(
            'acrisreallegal__documentid').only('documentid'))

        # clean filters, since the advanced search typically tacks on the property field
        # but we need the acrisreallegal field since we're going to be doing a subquery on it

        # subquery for acris real legals using the documenttype subquery
        filtered_acris = documenttype_queryset.filter(
            **date_filters).filter(**total_filters).only('bbl').filter(bbl=OuterRef('bbl'))

        queryset = queryset.annotate(has_filtered_acris=Exists(filtered_acris)).filter(has_filtered_acris=True)

        return queryset

    def filter_acrisrealmastersales_total_and_dates(self, queryset, name, values):

        date_filters, total_filters = self.parse_totaldate_field_values('documentid__docdate', 'documentid', values)
        documenttype_queryset = ds.AcrisRealLegal.objects.filter(
            documentid__in=ds.AcrisRealMaster.construct_sales_query('acrisreallegal__documentid')).only('documentid', 'bbl')

        # clean filters, since the advanced search typically tacks on the property field
        # but we need the acrisreallegal field since we're going to be doing a subquery on it

        # subquery for acris real legals using the documenttype subquery
        filtered_acris = documenttype_queryset.filter(
            **date_filters).filter(**total_filters).only('bbl').filter(bbl=OuterRef('bbl'))

        queryset = queryset.annotate(has_filtered_acris=Exists(filtered_acris)).filter(has_filtered_acris=True)

        return queryset

    def filter_dobpermitissued_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobissuedpermit__issuedate', 'dobissuedpermits', values)
        return queryset.filter(**date_filters).annotate(dobissuedpermits=Count('dobissuedpermit', distinct=True)).filter(**total_filters)

    def filter_eviction_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'eviction__executeddate', 'evictions', values)
        return queryset.filter(**date_filters).annotate(evictions=Count('eviction', distinct=True)).filter(**total_filters)

    # HPD Complaints

    def filter_hpdcomplaints_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'hpdcomplaint__receiveddate', 'hpdcomplaints', values)
        return queryset.filter(**date_filters).annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(**total_filters)

    def filter_hpdcomplaints_exact(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints=value)

    def filter_hpdcomplaints_gt(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gt=value)

    def filter_hpdcomplaints_gte(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gte=value).distinct()

    def filter_hpdcomplaints_lt(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lt=value)

    def filter_hpdcomplaints_lte(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lte=value)

    # HPD Violations
    def filter_hpdviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'hpdviolation__approveddate', 'hpdviolations', values)
        return queryset.filter(**date_filters).annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(**total_filters)

    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    def filter_hpdviolations_gt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gt=value)

    def filter_hpdviolations_gte(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gte=value)

    def filter_hpdviolations_lt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lt=value)

    def filter_hpdviolations_lte(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lte=value)

    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    # DOB Complaints
    def filter_dobcomplaints_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobcomplaint__dateentered', 'dobcomplaints', values)
        return queryset.filter(**date_filters).annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(**total_filters)

    def filter_dobcomplaints_exact(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints=value)

    def filter_dobcomplaints_gt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__gt=value)

    def filter_dobcomplaints_gte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__gte=value)

    def filter_dobcomplaints_lt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__lt=value)

    def filter_dobcomplaints_lte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('dobcomplaint', distinct=True)).filter(dobcomplaints__lte=value)

    # DOBViolations
    def filter_dobviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobviolation__issuedate', 'dobviolations', values)
        return queryset.filter(**date_filters).annotate(dobviolations=Count('dobviolation', distinct=True)).filter(**total_filters)

    def filter_dobviolations_exact(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations=value)

    def filter_dobviolations_gt(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gt=value)

    def filter_dobviolations_gte(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gte=value)

    def filter_dobviolations_lt(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lt=value)

    def filter_dobviolations_lte(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lte=value)

    # ECBViolations
    def filter_ecbviolations_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'ecbviolation__issuedate', 'ecbviolations', values)
        return queryset.filter(**date_filters).annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(**total_filters)

    def filter_ecbviolations_exact(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations=value)

    def filter_ecbviolations_gt(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gt=value)

    def filter_ecbviolations_gte(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gte=value)

    def filter_ecbviolations_lt(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lt=value)

    def filter_ecbviolations_lte(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lte=value)

    # Subsidy Program Names

    def filter_programnames(self, queryset, name, value):
        qs = []
        if value['exact']:
            return queryset.filter(**{name: value['exact']})
        if value['icontains']:
            return queryset.filter(**{"{}__icontains".format(name): value['icontains']})
        if value['any']:
            qs.append(reduce(operator.or_, (Q(**{name: item}) for item in value['any'])))
        if value['all']:
            qs.append(reduce(operator.and_, (Q(**{[name]: item}) for item in value['all'])))

        combined_q = reduce(operator.and_, (q for q in qs))

        return queryset.filter(combined_q)

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
