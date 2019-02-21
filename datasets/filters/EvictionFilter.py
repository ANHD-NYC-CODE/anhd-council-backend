import django_filters
from datasets import models as ds


class EvictionFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.Eviction
        fields = {
            'borough': ['exact'],
            'evictionaddress': ['exact', 'icontains'],
            'executeddate': ['exact', 'lt', 'lte', 'gt', 'gte']
        }
