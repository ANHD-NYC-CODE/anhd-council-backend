import django_filters
from datasets import models as ds


class PropertyAnnotationFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = ds.PropertyAnnotation
        fields = {
            'bbl': ['exact'],
            'aepstatus': ['exact', 'icontains'],
            'unitsrentstabilized': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'latestsaleprice': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdviolations_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdviolations_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdviolations_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdcomplaints_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdcomplaints_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'hpdcomplaints_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobviolations_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobviolations_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobviolations_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobcomplaints_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobcomplaints_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobcomplaints_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'ecbviolations_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'ecbviolations_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'ecbviolations_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'evictions_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'evictions_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'evictions_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobfiledpermits_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobfiledpermits_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobfiledpermits_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobissuedpermits_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobissuedpermits_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'dobissuedpermits_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'acrisrealmasters_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'acrisrealmasters_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'acrisrealmasters_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'housinglitigations_last30': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'housinglitigations_lastyear': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'housinglitigations_last3years': ['exact', 'lt', 'lte', 'gt', 'gte'],

        }
