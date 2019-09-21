import django_filters
from datasets import models as ds


class CoreSubsidyRecordFilter(django_filters.rest_framework.FilterSet):
    enddate__lte = django_filters.DateFilter(field_name='enddate', lookup_expr='lte')
    enddate__lt = django_filters.DateFilter(field_name='enddate', lookup_expr='lt')
    enddate = django_filters.DateFilter(field_name='enddate', lookup_expr='exact')
    enddate__gte = django_filters.DateFilter(field_name='enddate', lookup_expr='gte')
    enddate__gt = django_filters.DateFilter(field_name='enddate', lookup_expr='gt')

    class Meta:
        model = ds.CoreSubsidyRecord
        fields = {
            'programname': ['exact', 'iexact', 'icontains'],
        }
