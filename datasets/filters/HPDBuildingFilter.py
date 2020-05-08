import django_filters
from datasets import models as ds


class HPDBuildingFilter(django_filters.rest_framework.FilterSet):
    
    class Meta:
        model = ds.HPDBuildingRecord
        fields = {
            'bbl': ['isnull'],
            'bin': ['isnull'],
            'managementprogram': ['exact', 'icontains'],
            'legalclassa': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'legalclassb': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
