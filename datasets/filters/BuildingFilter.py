import django_filters
from datasets import models as ds


class BuildingFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.Building
        fields = {
            'lhnd': ['exact', 'iexact', 'icontains'],
            'hhnd': ['exact', 'iexact', 'icontains'],
            'stname': ['exact', 'iexact', 'icontains'],
        }
