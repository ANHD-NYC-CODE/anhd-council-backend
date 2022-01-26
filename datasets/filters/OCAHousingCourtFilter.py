import django_filters
from datasets import models as ds


class OCAHousingCourtFilter(django_filters.rest_framework.FilterSet):
    fileddate__lte = django_filters.DateFilter(
        field_name='fileddate', lookup_expr='lte')
    fileddate__lt = django_filters.DateFilter(
        field_name='fileddate', lookup_expr='lt')
    fileddate = django_filters.DateFilter(
        field_name='fileddate', lookup_expr='exact')
    fileddate__gte = django_filters.DateFilter(
        field_name='fileddate', lookup_expr='gte')
    fileddate__gt = django_filters.DateFilter(
        field_name='fileddate', lookup_expr='gt')

    class Meta:
        model = ds.OCAHousingCourt
        fields = {
            'bbl': ['isnull', 'exact'],
        }
