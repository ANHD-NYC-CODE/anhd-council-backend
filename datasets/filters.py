from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count, Q
import django_filters
from django import forms
from copy import deepcopy

HOUSING_TYPE_CHOICES = (
    (0, 'rs'),
    (1, 'rr'),
    (3, 'sh'),
    (4, 'mr'),
    (5, 'ph'),
)

from psycopg2.extras import DateRange


# class DateExactRangeWidget(django_filters.widgets.DateRangeWidget):
#     """Date widget to help filter by *_start and *_end."""
#     suffixes = ('start', 'end')


class TotalWithDateWidget(django_filters.widgets.SuffixedMultiWidget):
    """Date widget to help filter by *_start and *_end."""

    def __init__(self, attrs=None):
        widgets = (forms.DateInput, forms.DateInput, forms.NumberInput, forms.NumberInput,
                   forms.NumberInput, forms.NumberInput, forms.NumberInput)
        super().__init__(widgets, attrs)
    suffixes = ['start', 'end', 'lt', 'lte', 'exact', 'gt', 'gte']


class TotalWithDateField(django_filters.fields.RangeField):
    widget = TotalWithDateWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.DateField(),
            forms.DateField(),
            forms.IntegerField(),
            forms.IntegerField(),
            forms.IntegerField(),
            forms.IntegerField(),
            forms.IntegerField())

        super(TotalWithDateField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            start_date, end_date, lt_value, lte_value, exact_value, gt_value, gte_value = data_list
            filters = {
                'dates': (
                    {'__gte': start_date},
                    {'__lte': end_date},
                ),
                'totals': (
                    {'__lt': lt_value},
                    {'__lte': lte_value},
                    {'': exact_value},
                    {'__gt': gt_value},
                    {'__gte': gte_value}
                )
            }
            return filters


class TotalWithDateFilter(django_filters.Filter):
    """
    Filter to be used for Postgres specific Django field - DateRangeField.
    https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/#daterangefield
    """
    field_class = TotalWithDateField


class MultiQueryWidget(django_filters.widgets.SuffixedMultiWidget, django_filters.widgets.CSVWidget):
    """Date widget to help filter by *_start and *_end."""

    def __init__(self, attrs=None):
        widgets = (forms.TextInput, forms.TextInput, forms.TextInput)
        super().__init__(widgets, attrs)
    suffixes = ['0', '1', '2']


# class MultiQueryWidget(django_filters.widgets.CSVWidget):
#     suffixes = ['1', '2', '3']


class MultiQueryField(django_filters.fields.RangeField):
    widget = MultiQueryWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(),
            forms.CharField())
        super(MultiQueryField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        ##
        # Converts each querygroup into a dict for processing by filter.
        #
        # Example:
        # ?querygroup_1=hpdcomplaint_start=2018-01-01,hpdcomplaint_end=2019-12-31,hpdcomplaint_gte=5
        # converts to:
        # { 1: {hpdcomplaint: {start: '2018-01-01', end: '2019-12-31', gte: '5'}}
        ##
        if data_list:
            filter_groups = {}
            for index, group in enumerate(data_list):
                if not group:
                    continue
                filter_groups[index] = {}
                for query in group.split(','):
                    key = query.split('_')[0]
                    value_lookup = query.split('_')[1].split("=")[0]
                    value = query.split('=')[1]
                    if key in filter_groups[index]:
                        filter_groups[index][key][value_lookup] = value
                    else:
                        filter_groups[index][key] = {}
                        filter_groups[index][key][value_lookup] = value
            return filter_groups


class MultiQueryFilter(filters.Filter):
    field_class = MultiQueryField

    # def __init__(self, *args, **kwargs):
    #     super(MultiQueryFilter, self).__init__(*args, **kwargs)


class PropertyFilter(django_filters.rest_framework.FilterSet):
    @property
    def qs(self):
        return super(PropertyFilter, self).qs\
            .prefetch_related('hpdcomplaint_set')\
            .prefetch_related('hpdviolation_set')\

    querygroup = MultiQueryFilter(method='filter_querygroups')

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

    # querygroups

    def filter_querygroups(self, queryset, name, values):
        def format_value(self, filter, value):
            ##
            # Makes sure that the value passed to the filter is padded with Null values
            # corresponding to the widget suffixes
            ##
            v = ()
            for suffix in filter.field.widget.suffixes:
                if suffix in value.keys():
                    v = v + (value[suffix],)
                else:
                    v = v + (None,)
            return v

        qs = []
        for groupkey, groupvalue in values.items():

            gqs = deepcopy(queryset)
            for key, value in groupvalue.items():
                formatted_value = format_value(self, self.filters[key], value)
                # chains querysets on AND
                gqs = self.filters[key].filter(
                    gqs, self.filters[key].field.compress(formatted_value))

            qs.append(gqs)

        # perform all queries, combine + return only unique records from all queries
        return qs.pop().union(*qs)

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
    # SLOW
    def filter_dobcomplaints_exact(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints=value)

    def filter_dobcomplaints_gt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__gt=value)

    def filter_dobcomplaints_gte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__gte=value)

    def filter_dobcomplaints_lt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__lt=value)

    def filter_dobcomplaints_lte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__lte=value)

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
        fields = ['querygroup', 'yearbuilt', 'council', 'hpdcomplaints',
                  'hpdviolations', 'dobviolations', 'ecbviolations']
