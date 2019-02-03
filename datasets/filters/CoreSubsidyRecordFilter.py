import django_filters
from datasets import models as ds


class CoreSubsidyRecordFilter(django_filters.rest_framework.FilterSet):
    enddate__lte = django_filters.DateFilter(field_name='enddate', lookup_expr='date__lte')
    enddate__lt = django_filters.DateFilter(field_name='enddate', lookup_expr='date__lt')
    enddate = django_filters.DateFilter(field_name='enddate', lookup_expr='date__exact')
    enddate__gte = django_filters.DateFilter(field_name='enddate', lookup_expr='date__gte')
    enddate__gt = django_filters.DateFilter(field_name='enddate', lookup_expr='date__gt')

    class Meta:
        model = ds.CoreSubsidyRecord
        fields = {
            'programname': ['exact', 'iexact', 'icontains'],
        }
