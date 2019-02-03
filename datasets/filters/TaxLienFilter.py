import django_filters
from datasets import models as ds


class TaxLienFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.TaxLien
        fields = {
            'year': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
