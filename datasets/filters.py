from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count


class PropertyFilter(filters.FilterSet):
    hpdviolations = filters.NumberFilter(name="HPD Filters", method='filter_hpdviolations_exact', lookup_expr='exact')
    hpdviolations__gt = filters.NumberFilter(method='filter_hpdviolations_gt')
    hpdviolations__lt = filters.NumberFilter(method='filter_hpdviolations_lt')
    housingtype = filters.CharFilter(method='filter_housingtype')

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
