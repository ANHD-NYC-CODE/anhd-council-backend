from datasets import models as ds
from django_filters.rest_framework import FilterSet


class PropertyFilter(FilterSet):
    class Meta:
        model = ds.Property
        fields = {
            'yearbuilt': ['exact', 'lt', 'gt'],
        }
