from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count, Q, OuterRef, Subquery, ExpressionWrapper, F, FloatField
from django.db.models.functions import Cast
import django_filters
from django import forms
from copy import deepcopy
from datasets.filter_helpers import TotalWithDateFilter, RSLostPercentWithDateFilter, AdvancedQueryFilter
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

    def parse_values(self, values):
        v = ()
        for value in values.split(' '):
            v = v + ({
                'type': value.split('_', 1)[0].lower(),
                'id': value.split('_', 1)[1].split('=')[0].lower(),
                'value': value.split('=', 1)[1].lower(),
                'dataset': value.split('=', 1)[1].split(',')[0].split('__', 1)[0].lower()
            },)
        return v

    def read_criteria_options(self, criteria, values):
        options = ()
        for value in values:
            if 'option' in value['type'] and criteria['id'] in value['id']:
                options = options + (value,)
        return options

    def get_next_criteria(self, category_id, values):
        for value in values:
            if 'criteria' in value['type'] and value['id'] == category_id:
                return value

    def construct_rule_query(self, option, counts=False):
        parameters = {}
        for parameter in option['value'].split(','):
            par = parameter.split('=')
            if counts:
                if 'count' in parameter or 'percent' in parameter:
                    parameters[par[0]] = par[1]
            elif counts == False:
                if not 'count' in parameter and not 'percent' in parameter:
                    parameters[par[0]] = par[1]
        return parameters

    def construct_option_query(self, option, values, counts=False):
        if '*criteria' in option['value']:
            next_id = option['value'].partition('_')[2]
            if not next_id:
                raise Exception("Malformed Query - an option's criteria format should be like: '*criteria_0'")
            next_criteria = self.get_next_criteria(next_id, values)
            q_value = self.read_criteria(next_criteria, values, counts)
        else:
            q_value = Q(**self.construct_rule_query(option, counts))
            self.q_filters.append({'dataset': option['value'].split('__')[0], 'q': q_value})
        return q_value

    def read_criteria(self, criteria, values, counts=False):
        if criteria['value'].lower() == 'all':
            q_op = Q.AND
        elif criteria['value'].lower() == 'any':
            q_op = Q.OR
        else:
            raise Exception('invalid criteria: {}'.format(criteria))

        query = None
        options = self.read_criteria_options(criteria, values)
        or_list = []  # for construcing new Q statements as an OR without default AND

        for option in options:
            if not query and q_op == Q.OR:
                or_list.append(Q(self.construct_option_query(option, values, counts)))
            elif not query and q_op == Q.AND:
                query = Q(self.construct_option_query(option, values, counts))
            else:
                q_filter = self.construct_option_query(option, values, counts)
                query.add(q_filter, q_op)

        # Constructs a Q entirely of ORs and removes the initial AND
        if q_op == Q.OR:
            query = or_list.pop()

            for item in or_list:
                query |= item

        return query

    def get_dataset_count_annotation(self, count_key, q_filter):
        return {
            count_key: Count(
                q_filter['dataset'],
                filter=q_filter['q'],
                distinct=True
            )
        }

    # advanced query
    # http://localhost:8000/councils/6/properties/?housingtype=rs&q=criteria_0=ALL+option_0A=*criteria_1+option_0B=rentstabilizationrecord__uc2007__gte=0,rentstabilizationrecord__uc2017__gte=0,rentstabilizationrecords__percent__gte=0.5+criteria_1=ANY+option_1A=dobviolation__issuedate__gte=2017-01-01,dobviolation__issuedate__lte=2018-01-01,dobviolations__count__gte=1+option_1B=ecbviolation__issuedate__gte=2017-01-01,ecbviolation__issuedate__lte=2018-01-01,ecbviolations__count__gte=1
    def filter_advancedquery(self, queryset, name, values):
        # 1) filter queryset by model fields first
        # return queryset with only BBL values (to reduce memory overhead)
        # 2) perform related Q query on date ranges, other ranges
        # return queryset with only BBL values
        # 3) perform related Q query on counts
        # return queryset with all values

        parsed_values = self.parse_values(values)
        dates_q = Q(self.read_criteria(
            parsed_values[0], parsed_values, False))

        # 1
        initial_bbls = queryset.only('bbl').values('bbl')
        filtered_by_model_queryset = ds.Property.objects.filter(bbl__in=initial_bbls)

        # 2
        related_queryset = filtered_by_model_queryset.only('bbl').filter(dates_q).distinct()

        for q_filter in self.q_filters:
            # Prefetch related datasets and annotate counts

            if q_filter['dataset'].lower() not in (model.lower() for model in settings.ACTIVE_MODELS):
                continue

            # option_0B=rentstabilizationrecord__uc2007__gte=0,rentstabilizationrecord__uc2017__gte=0,rentstabilizationrecords__percent__gte=0.2,rentstabilizationrecords__percent__lte=1
            # props.council(1).annotate(rslostpercent=ExpressionWrapper(1 - Cast(F('rs2017'), FloatField()) / Cast(F('rs2007'), FloatField()), output_field=FloatField())).filter(rslostpercent__gte=0.9)
            if q_filter['dataset'] == 'rentstabilizationrecord':
                rsvalues = list(filter(lambda x: x['dataset'] == 'rentstabilizationrecord', parsed_values))[
                    0]['value'].split(',')
                try:
                    start_year = rsvalues[0].split('__', 2)[1].split('uc', 1)[1]
                    end_year = rsvalues[1].split('__', 2)[1].split('uc', 1)[1]
                    related_queryset = related_queryset.annotate(**{'rentstabilizationrecord' + start_year: F('rentstabilizationrecord__uc' + start_year)}).annotate(**{
                        'rentstabilizationrecord' + end_year: F('rentstabilizationrecord__uc' + end_year)})
                    related_queryset = related_queryset.annotate(
                        rentstabilizationrecords__percent=ExpressionWrapper(
                            1 - Cast(F('rentstabilizationrecord' + end_year), FloatField()) /
                            Cast(F('rentstabilizationrecord' + start_year), FloatField()), output_field=FloatField()
                        )
                    )
                except Exception as e:
                    raise Exception("Malformed rentstabilization parameter. Error: {}".format(e))
            else:
                count_key = q_filter['dataset'] + 's__count'
                related_queryset = related_queryset.prefetch_related(q_filter['dataset'] + '_set').annotate(
                    **self.get_dataset_count_annotation(count_key, q_filter)
                )

            ##
            # Less memory intensive, but less efficient query.
            #
            # Uses a subquery - 1 query per result in related_queryset -
            # this saves on Postgres memory and speeds things up
            # even if inefficient, if lieu of scaled resources.
            #
            # But it turns out increasing the cache and work_mem of postgres
            # in the config fixes the slowness!
            ##
            # related_queryset = related_queryset.annotate(
            #     **{count_key: Subquery(
            #         ds.Property.objects.filter(
            #             bbl=OuterRef('bbl')
            #         ).annotate(
            #             sub_count=Count(
            #                 q_filter['dataset'],
            #                 filter=q_filter['q'],
            #                 distinct=True
            #             )
            #         ).values('sub_count')[:1]
            #     )
            #     }
            # )

        # 3
        count_q = Q(self.read_criteria(parsed_values[0], parsed_values, True))
        final_bbls = related_queryset.filter(count_q).only('bbl').values('bbl')
        return ds.Property.objects.filter(bbl__in=final_bbls)

    # Rent stabilized units lost
    def filter_stabilizedunitslost_percent_and_dates(self, queryset, name, values):
        return queryset.rs_annotate().annotate(rslostpercent=ExpressionWrapper(1 - Cast(F(values['end_year']), FloatField()) / Cast(F(values['start_year']), FloatField()), output_field=FloatField())).filter(**values['percent_query'])

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
            'yearbuilt': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'unitsres': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'unitstotal': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'bldgclass': ['exact'],
            'numbldgs': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'numfloors': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
