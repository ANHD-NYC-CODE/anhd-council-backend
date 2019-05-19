import django_filters
import rest_framework_filters as filters
from django import forms
from datasets import models as ds
from django.db.models import Count, FilteredRelation, Q, Subquery, OuterRef, IntegerField, F
from datasets.utils import advanced_filter as af


def property_dataset_annotation_key(model_name):
    if model_name == 'acrisrealmaster':
        return 'acrisreallegals'
    else:
        return model_name.lower() + 's'


def value_dict_to_date_filter_dict(date_prefix, values):
    ####
    # Converts {dates: ({'__gte': 2018-01-01})}
    # to
    # {'hpdviolation__approveddate__gte': datetime.date(2018, 1, 1)}
    date_filters = {}
    for item in values['dates']:
        for k, v in item.items():
            if v is not None:
                date_filters[date_prefix + k] = v
    return date_filters


def filtered_dataset_annotation(dataset_prefix, date_filters, queryset):
    filtered_key = dataset_prefix + '_filtered'
    bbl_key = dataset_prefix + '__bbl__in'
    dataset_plural_key = dataset_prefix + 's'

    # Slower due to:
    # ** with bbl__in
    # ** with count distinct
    # queryset = queryset.annotate(**{filtered_key: FilteredRelation(dataset_prefix, condition=Q(
    #     af.construct_and_q([date_filters]), Q(**{bbl_key: queryset.values('bbl')})))})
    # queryset = queryset.annotate(**{dataset_plural_key: Count(filtered_key, distinct=True)})

    if dataset_prefix == 'acrisrealmaster':
        acrislegals = ds.AcrisRealLegal.objects.filter(bbl=OuterRef('bbl'))
        queryset = queryset.annotate(**{dataset_plural_key: Count('acrisreallegal', filter=Q(
            Q(acrisreallegal__documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES), af.construct_and_q([date_filters])), distinct=True)})
    else:
        queryset = queryset.annotate(**{filtered_key: FilteredRelation(dataset_prefix, condition=Q(
            af.construct_and_q([date_filters])))})
        # Slower due to:
        # Join table GROUP BY with many large datasets
        queryset = queryset.annotate(**{dataset_plural_key: Count(filtered_key, distinct=True)})

    # abandoned due to unexplained hang
    # queryset = queryset.annotate(**{dataset_plural_key: Count(dataset_prefix,
    #                                                           filter=af.construct_and_q([date_filters]), distinct=True)})

    return queryset


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


class CommaSeparatedConditionWidget(django_filters.widgets.SuffixedMultiWidget):
    """Character widget parsing comma separated values. ex: param__any=1,2,3"""

    def __init__(self, attrs=None):
        widgets = (forms.TextInput, forms.TextInput, forms.TextInput, forms.TextInput,)
        super().__init__(widgets, attrs)
    suffixes = ['_any', '_all', '', '_icontains']


class CommaSeparatedConditionField(django_filters.fields.RangeField):
    widget = CommaSeparatedConditionWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(), forms.CharField(),  forms.CharField(), forms.CharField(),)

        super(CommaSeparatedConditionField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            data = {'any': None, 'all': None, 'exact': None, 'icontains': None}
            any, all, exact, icontains = data_list
            if exact:
                data['exact'] = exact
                return data
            if icontains:
                data['icontains'] = icontains
            if any:
                any = any.split(',')
                any = list(map(lambda x: x.strip(), any))
                data['any'] = any
                # data.append(reduce(operator.or_, (Q(*{[name]: item}) for item in any)))
            if all:
                all = all.split(',')
                all = list(map(lambda x: x.strip(), all))
                data['all'] = all
                # data.append(reduce(operator.or_, (Q(*{[name]: item}) for item in all)))
            return data


class CommaSeparatedConditionFilter(django_filters.Filter):
    field_class = CommaSeparatedConditionField


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
            if lt_value or lt_value == 0:
                queries['rslostpercent__lt'] = lt_value
            if lte_value or lte_value == 0:
                queries['rslostpercent__lte'] = lte_value
            if exact_value or exact_value == 0:
                queries['rslostpercent'] = exact_value
            if gt_value or gt_value == 0:
                queries['rslostpercent__gt'] = gt_value
            if gte_value or gte_value == 0:
                queries['rslostpercent__gte'] = gte_value

            return queries

        if data_list:
            start_year, end_year, lt_value, lte_value, exact_value, gt_value, gte_value = data_list
            if not end_year:
                if ds.RentStabilizationRecord.get_dataset():
                    end_year = ds.RentStabilizationRecord.get_dataset().latest_version() or '2017'
                else:
                    end_year = '2017'

            filters = {
                'start_year': 'rentstabilizationrecord__uc{}'.format(start_year),
                'end_year': 'rentstabilizationrecord__uc{}'.format(end_year),
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
