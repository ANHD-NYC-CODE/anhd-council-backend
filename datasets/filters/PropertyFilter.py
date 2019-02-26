from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField
from django.db.models.functions import Cast
import django_filters
from django import forms
from copy import deepcopy
from datasets.filter_helpers import construct_or_q, TotalWithDateFilter, RSLostPercentWithDateFilter, AdvancedQueryFilter
from datasets.utils import advanced_filter as af

from collections import OrderedDict
from django.conf import settings
from psycopg2.extras import DateRange


class PropertyFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        self.q_filters = []
        return super(PropertyFilter, self).__init__(*args, **kwargs)

    @property
    def qs(self):
        return super(PropertyFilter, self).qs

    q = AdvancedQueryFilter(method='filter_advancedquery')

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

    dobpermitissuedjoined = TotalWithDateFilter(method="filter_dobpermitissuedjoined_total_and_dates")
    evictions = TotalWithDateFilter(method="filter_eviction_total_and_dates")

    taxlien = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='exact')
    taxlien__lt = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='lt')
    taxlien__lte = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='lte')
    taxlien__gt = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='gt')
    taxlien__gte = django_filters.NumberFilter(field_name='taxlien__year', lookup_expr='gte')

    subsidy__enddate__lte = django_filters.DateFilter(field_name='coresubsidyrecord__enddate', lookup_expr='date__lte')
    subsidy__enddate__lt = django_filters.DateFilter(field_name='coresubsidyrecord__enddate', lookup_expr='date__lt')
    subsidy__enddate = django_filters.DateFilter(field_name='coresubsidyrecord__enddate', lookup_expr='date__exact')
    subsidy__enddate__gte = django_filters.DateFilter(field_name='coresubsidyrecord__enddate', lookup_expr='date__gte')
    subsidy__enddate__gt = django_filters.DateFilter(field_name='coresubsidyrecord__enddate', lookup_expr='date__gt')
    subsidy__programname = django_filters.CharFilter(
        field_name='coresubsidyrecord__programname', lookup_expr='icontains')

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
        switcher = {
            "rs": queryset.rentstab(),
            "rr": queryset.rentreg(),
            "sh": queryset.smallhome(),
            "mr": queryset.marketrate(),
            "ph": queryset.publichousing()
        }
        return switcher.get(value, queryset.none())

    def filter_advancedquery(self, queryset, name, values):
        mappings = af.convert_query_string_to_mapping(values)

        # filter on non-annotating filters (like dates)
        q1 = af.convert_condition_to_q(mappings[0], mappings, 'query1_filters')
        q1_queryset = queryset.only('bbl').filter(q1).distinct()

        # filter on annotating filters (like counts)
        q2 = af.convert_condition_to_q(mappings[0], mappings, 'query2_filters')
        for condition in mappings:
            for c_filter in condition['filters']:
                if 'condition' in c_filter:
                    continue
                if c_filter['model'].lower() not in (model.lower() for model in settings.ACTIVE_MODELS):
                    continue

                if c_filter['model'] == 'rentstabilizationrecord':
                    q1_queryset = af.annotate_rentstabilized(q1_queryset, c_filter)
                elif c_filter['model'].lower() == 'acrisreallegal':
                    q1_queryset = q1_queryset.filter(
                        ds.AcrisRealMaster.construct_sales_query('acrisreallegal__documentid'))
                    if c_filter['annotation_key']:
                        q1_queryset = q1_queryset.annotate(**{c_filter['annotation_key']: Count(
                            c_filter['model'],
                            filter=af.construct_and_q(c_filter['query1_filters']),
                            distinct=True
                        )})
                else:
                    q1_queryset = q1_queryset.prefetch_related(c_filter['prefetch_key'])
                    if c_filter['annotation_key']:
                        q1_queryset = q1_queryset.annotate(**{c_filter['annotation_key']: Count(
                            c_filter['model'],
                            filter=af.construct_and_q(c_filter['query1_filters']),
                            distinct=True
                        )})

        q2_queryset = q1_queryset.only('bbl').filter(q2).distinct()
        final_bbls = q2_queryset.values('bbl')

        return ds.Property.objects.filter(bbl__in=final_bbls)

    # Rent stabilized units lost

    def filter_stabilizedunitslost_percent_and_dates(self, queryset, name, values):
        return queryset.rs_annotate().annotate(rslostpercent=ExpressionWrapper(1 - Cast(F(values['end_year']), FloatField()) / Cast(F(values['start_year']), FloatField()), output_field=FloatField())).filter(**values['percent_query'])

    def filter_acrisrealmasteramounts_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'acrisreallegal__documentid__docdate', 'acrisreallegal__documentid__docamount', values)
        return queryset.filter(**date_filters).annotate(acrisrealmasters=Count('acrisreallegal__documentid', filter=Q(**total_filters), distinct=True)).filter(acrisrealmasters__gte=1)

    def filter_acrisrealmastersales_total_and_dates(self, queryset, name, values):

        q_list = []
        for type in ds.AcrisRealMaster.SALE_DOC_TYPES:
            q_list.append(Q(**{'acrisreallegal__documentid__doctype': type}))

        date_filters, total_filters = self.parse_totaldate_field_values(
            'acrisreallegal__documentid__docdate', 'acrisrealmasters', values)
        return queryset.filter(**date_filters).annotate(acrisrealmasters=Count('acrisreallegal__documentid', filter=ds.AcrisRealMaster.construct_sales_query('acrisreallegal__documentid'), distinct=True)).filter(**total_filters)

    def filter_dobpermitissuedjoined_total_and_dates(self, queryset, name, values):
        date_filters, total_filters = self.parse_totaldate_field_values(
            'dobpermitissuedjoined__issuedate', 'dobpermitissuedjoineds', values)
        return queryset.filter(**date_filters).annotate(dobpermitissuedjoineds=Count('dobpermitissuedjoined', distinct=True)).filter(**total_filters)

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

    class Meta:
        model = ds.Property
        fields = {
            'council': ['exact'],
            'cd': ['exact'],
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
