import django_filters
import rest_framework_filters as filters
from django import forms


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


class AdvancedQueryField(forms.Field):
    # widget = TotalWithDateWidget

    def __init__(self, *args, **kwargs):
        super(AdvancedQueryField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        if data_list:
            import pdb
            pdb.set_trace()


class AdvancedQueryFilter(django_filters.Filter):
    field_class = AdvancedQueryField
