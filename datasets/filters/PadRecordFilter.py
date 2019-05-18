import django_filters
from datasets import models as ds


class PadRecordFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.PadRecord
        fields = {
            'lhnd': ['exact', 'iexact', 'icontains'],
            'hhnd': ['exact', 'iexact', 'icontains'],
            'stname': ['exact', 'iexact', 'icontains']
        }
