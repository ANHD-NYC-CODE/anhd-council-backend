import django_filters
import rest_framework_filters as filters
from django import forms


class TotalWithDateWidget(django_filters.widgets.SuffixedMultiWidget):
    """Date widget to help filter by *_start and *_end."""

    def __init__(self, attrs=None):
        widgets = (forms.DateInput, forms.DateInput, forms.NumberInput, forms.NumberInput,
                   forms.NumberInput, forms.NumberInput, forms.NumberInput)
        super().__init__(widgets, attrs)
    suffixes = ['_start', '_end', '_lt', '_lte', '_exact', '_gt', '_gte']


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


class PercentWithDateWidget(django_filters.widgets.SuffixedMultiWidget):
    """Date widget to help filter by *_start and *_end."""

    def __init__(self, attrs=None):
        widgets = (forms.DateInput, forms.DateInput, forms.NumberInput, forms.NumberInput,
                   forms.NumberInput, forms.NumberInput, forms.NumberInput)
        super().__init__(widgets, attrs)
    suffixes = ['_start', '_end', '_lt', '_lte', '_exact', '_gt', '_gte']


class PercentWithDateField(django_filters.fields.RangeField):
    widget = PercentWithDateWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.IntegerField(),
            forms.FloatField(),
            forms.FloatField(),
            forms.FloatField(),
            forms.FloatField(),
            forms.FloatField()
        )

        super(PercentWithDateField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        def get_percent_query():
            queries = {}
            if lt_value:
                queries['rslostpercent__lt'] = lt_value
            if lte_value:
                queries['rslostpercent__lte'] = lte_value
            if exact_value:
                queries['rslostpercent'] = exact_value
            if gt_value:
                queries['rslostpercent__gt'] = gt_value
            if gte_value:
                queries['rslostpercent__gte'] = gte_value

            return queries

        if data_list:
            start_year, end_year, lt_value, lte_value, exact_value, gt_value, gte_value = data_list
            filters = {
                'start_year': 'rentstabilizationrecord{}'.format(start_year),
                'end_year': 'rentstabilizationrecord{}'.format(end_year),
                'percent_query': get_percent_query()
            }

            return filters


class RSLostPercentWithDateFilter(django_filters.Filter):
    """
    Filter to be used for Postgres specific Django field - DateRangeField.
    https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/#daterangefield
    """
    field_class = PercentWithDateField


class AdvancedQueryField(forms.Field):
    # widget = TotalWithDateWidget

    def __init__(self, *args, **kwargs):
        super(AdvancedQueryField, self).__init__(*args, **kwargs)


class AdvancedQueryFilter(django_filters.Filter):
    field_class = AdvancedQueryField


def construct_or_q(query_list):
    query = query_list.pop()

    for item in query_list:
        query |= item

    return query


def construct_and_q(query_list):
    query = query_list.pop()
    for item in query_list:
        query &= item

    return query
