from datasets import models as ds
from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from django.db.models import Count


class PropertyFilter(FilterSet):
    hpdviolations = NumberFilter(method='filter_hpdviolations_exact', lookup_expr='exact')
    hpdviolations__gt = NumberFilter(method='filter_hpdviolations_gt')
    hpdviolations__lt = NumberFilter(method='filter_hpdviolations_lt')
    housingtype = CharFilter(method='filter_housingtype')

    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    def filter_hpdviolations_gt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gt=value)

    def filter_hpdviolations_lt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lt=value)

    def filter_housingtype(self, queryset, name, value):
        switcher = {
            "rs": queryset.rentstab(),
            "rr": queryset.rentreg(),
            "sh": queryset.smallhome(),
            "mr": queryset.marketrate()
        }
        return switcher.get(value, queryset)

    class Meta:
        model = ds.Property
        fields = {
            'yearbuilt': ['exact', 'lt', 'gt'],
            'council': ['exact']

        }
