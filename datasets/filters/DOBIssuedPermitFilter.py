import django_filters
from datasets import models as ds


class DOBIssuedPermitFilter(django_filters.rest_framework.FilterSet):
    issuedate__lte = django_filters.DateFilter(
        field_name='issuedate', lookup_expr='date__lte')
    issuedate__lt = django_filters.DateFilter(
        field_name='issuedate', lookup_expr='date__lt')
    issuedate = django_filters.DateFilter(
        field_name='issuedate', lookup_expr='date__exact')
    issuedate__gte = django_filters.DateFilter(
        field_name='issuedate', lookup_expr='date__gte')
    issuedate__gt = django_filters.DateFilter(
        field_name='issuedate', lookup_expr='date__gt')

    class Meta:
        model = ds.DOBIssuedPermit
        fields = {
            'key': ['exact'],
            'jobfilingnumber': ['exact'],
            'workpermit': ['exact'],
            'bbl': ['isnull'],
            'bin': ['isnull'],
            'worktype': ['exact', 'icontains'],
            'jobdescription': ['exact', 'icontains'],
            'foreign_key': ['exact'],
            'type': ['exact', 'icontains'],
        }
