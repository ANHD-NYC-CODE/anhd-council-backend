import django_filters
from datasets import models as ds


class EvictionFilter(django_filters.rest_framework.FilterSet):
    executeddate__lte = django_filters.DateFilter(
        field_name='executeddate', lookup_expr='lte')
    executeddate__lt = django_filters.DateFilter(
        field_name='executeddate', lookup_expr='lt')
    executeddate = django_filters.DateFilter(
        field_name='executeddate', lookup_expr='exact')
    executeddate__gte = django_filters.DateFilter(
        field_name='executeddate', lookup_expr='gte')
    executeddate__gt = django_filters.DateFilter(
        field_name='executeddate', lookup_expr='gt')

    class Meta:
        model = ds.Eviction
        fields = {
            'bbl': ['isnull', 'exact'],
            'borough': ['exact'],
            'evictionaddress': ['exact', 'icontains'],
            'cleaned_address': ['exact', 'icontains', 'isnull'],
            'geosearch_address': ['exact', 'icontains', 'isnull'],
        }
