from datasets import models as ds
from django_filters.rest_framework import FilterSet, NumberFilter
from django.db.models import Count


class PropertyFilter(FilterSet):
    hpdviolations = NumberFilter(method='filter_hpdviolations_exact')
    hpdviolations__gt = NumberFilter(method='filter_hpdviolations_gt')

    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    def filter_hpdviolations_gt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gt=value)

    class Meta:
        model = ds.Property
        fields = {
            'yearbuilt': ['exact', 'lt', 'gt'],
            'council': ['exact']

        }
