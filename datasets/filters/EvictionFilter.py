import django_filters
from datasets import models as ds


class EvictionFilter(django_filters.rest_framework.FilterSet):
    executeddate__lte = django_filters.DateFilter(field_name='executeddate', lookup_expr='date__lte')
    executeddate__lt = django_filters.DateFilter(field_name='executeddate', lookup_expr='date__lt')
    executeddate = django_filters.DateFilter(field_name='executeddate', lookup_expr='date__exact')
    executeddate__gte = django_filters.DateFilter(field_name='executeddate', lookup_expr='date__gte')
    executeddate__gt = django_filters.DateFilter(field_name='executeddate', lookup_expr='date__gt')

    class Meta:
        model = ds.Eviction
        fields = {
            'bbl': ['exact', 'isnull'],
            'borough': ['exact'],
            'evictionaddress': ['exact', 'icontains'],
            'cleaned_address': ['exact', 'icontains', 'isnull'],
            'geosearch_address': ['exact', 'icontains', 'isnull'],
        }
