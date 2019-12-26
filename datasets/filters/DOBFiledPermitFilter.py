import django_filters
from datasets import models as ds


class DOBFiledPermitFilter(django_filters.rest_framework.FilterSet):
    datefiled__lte = django_filters.DateFilter(
        field_name='datefiled', lookup_expr='date__lte')
    datefiled__lt = django_filters.DateFilter(
        field_name='datefiled', lookup_expr='date__lt')
    datefiled = django_filters.DateFilter(
        field_name='datefiled', lookup_expr='date__exact')
    datefiled__gte = django_filters.DateFilter(
        field_name='datefiled', lookup_expr='date__gte')
    datefiled__gt = django_filters.DateFilter(
        field_name='datefiled', lookup_expr='date__gt')

    class Meta:
        model = ds.DOBFiledPermit
        fields = {
            'jobfilingnumber': ['exact', 'isnull'],
            'bbl': ['isnull'],
            'bin': ['exact', 'isnull'],
            'jobtype': ['exact', 'icontains'],
            'jobdescription': ['exact', 'icontains'],
            'jobstatus': ['exact', 'icontains'],
            'foreign_key': ['exact'],
            'type': ['exact', 'icontains'],
        }
