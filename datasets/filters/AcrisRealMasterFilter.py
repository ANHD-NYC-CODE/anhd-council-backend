import django_filters
from datasets import models as ds


class AcrisRealMasterFilter(django_filters.rest_framework.FilterSet):
    docdate__lte = django_filters.DateFilter(field_name='docdate', lookup_expr='date__lte')
    docdate__lt = django_filters.DateFilter(field_name='docdate', lookup_expr='date__lt')
    docdate = django_filters.DateFilter(field_name='docdate', lookup_expr='date__exact')
    docdate__gte = django_filters.DateFilter(field_name='docdate', lookup_expr='date__gte')
    docdate__gt = django_filters.DateFilter(field_name='docdate', lookup_expr='date__gt')

    class Meta:
        model = ds.AcrisRealMaster
        fields = {
            'docamount': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'doctype': ['exact', 'iexact', 'icontains']
        }
