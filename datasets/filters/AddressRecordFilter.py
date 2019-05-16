import django_filters
from datasets import models as ds


class AddressRecordFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.AddressRecord
        fields = {
            'pad_address': ['exact', 'iexact', 'icontains'],
            'street': ['exact', 'iexact', 'icontains'],
            'number': ['exact', 'iexact', 'icontains'],
            'borough': ['exact'],
            'zipcode': ['exact']
        }
