from datasets import models as ds
import rest_framework_filters as filters
from django.db.models import Count


class PropertyFilter(filters.FilterSet):
    housingtype = filters.CharFilter(method='filter_housingtype')

    hpdcomplaints = filters.NumberFilter(method='filter_hpdcomplaints_exact')
    hpdcomplaints__gt = filters.NumberFilter(method='filter_hpdcomplaints_gt')
    hpdcomplaints__gte = filters.NumberFilter(method='filter_hpdcomplaints_gte')
    hpdcomplaints__lt = filters.NumberFilter(method='filter_hpdcomplaints_lt')
    hpdcomplaints__lte = filters.NumberFilter(method='filter_hpdcomplaints_lte')

    hpdviolations = filters.NumberFilter(method='filter_hpdviolations_exact')
    hpdviolations__gt = filters.NumberFilter(method='filter_hpdviolations_gt')
    hpdviolations__gte = filters.NumberFilter(method='filter_hpdviolations_gte')
    hpdviolations__lt = filters.NumberFilter(method='filter_hpdviolations_lt')
    hpdviolations__lte = filters.NumberFilter(method='filter_hpdviolations_lte')

    dobcomplaints = filters.NumberFilter(method='filter_dobcomplaints_exact')
    dobcomplaints__gt = filters.NumberFilter(method='filter_dobcomplaints_gt')
    dobcomplaints__gte = filters.NumberFilter(method='filter_dobcomplaints_gte')
    dobcomplaints__lt = filters.NumberFilter(method='filter_dobcomplaints_lt')
    dobcomplaints__lte = filters.NumberFilter(method='filter_dobcomplaints_lte')

    dobviolations = filters.NumberFilter(method='filter_dobviolations_exact')
    dobviolations__gt = filters.NumberFilter(method='filter_dobviolations_gt')
    dobviolations__gte = filters.NumberFilter(method='filter_dobviolations_gte')
    dobviolations__lt = filters.NumberFilter(method='filter_dobviolations_lt')
    dobviolations__lte = filters.NumberFilter(method='filter_dobviolations_lte')

    ecbviolations = filters.NumberFilter(method='filter_ecbviolations_exact')
    ecbviolations__gt = filters.NumberFilter(method='filter_ecbviolations_gt')
    ecbviolations__gte = filters.NumberFilter(method='filter_ecbviolations_gte')
    ecbviolations__lt = filters.NumberFilter(method='filter_ecbviolations_lt')
    ecbviolations__lte = filters.NumberFilter(method='filter_ecbviolations_lte')

    def filter_housingtype(self, queryset, name, value):
        switcher = {
            "rs": queryset.rentstab(),
            "rr": queryset.rentreg(),
            "sh": queryset.smallhome(),
            "mr": queryset.marketrate()
        }
        return switcher.get(value, queryset.none())

    # HPD Complaints

    def filter_hpdcomplaints_exact(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints=value)

    def filter_hpdcomplaints_gt(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gt=value)

    def filter_hpdcomplaints_gte(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__gte=value)

    def filter_hpdcomplaints_lt(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lt=value)

    def filter_hpdcomplaints_lte(self, queryset, name, value):
        return queryset.annotate(hpdcomplaints=Count('hpdcomplaint', distinct=True)).filter(hpdcomplaints__lte=value)

    # HPD Violations
    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    def filter_hpdviolations_gt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gt=value)

    def filter_hpdviolations_gte(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__gte=value)

    def filter_hpdviolations_lt(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lt=value)

    def filter_hpdviolations_lte(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations__lte=value)

    def filter_hpdviolations_exact(self, queryset, name, value):
        return queryset.annotate(hpdviolations=Count('hpdviolation', distinct=True)).filter(hpdviolations=value)

    # DOB Complaints
    # SLOW
    def filter_dobcomplaints_exact(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints=value)

    def filter_dobcomplaints_gt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__gt=value)

    def filter_dobcomplaints_gte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__gte=value)

    def filter_dobcomplaints_lt(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__lt=value)

    def filter_dobcomplaints_lte(self, queryset, name, value):
        return queryset.annotate(dobcomplaints=Count('building__dobcomplaint', distinct=True)).filter(dobcomplaints__lte=value)

    # DOBViolations

    def filter_dobviolations_exact(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations=value)

    def filter_dobviolations_gt(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gt=value)

    def filter_dobviolations_gte(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__gte=value)

    def filter_dobviolations_lt(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lt=value)

    def filter_dobviolations_lte(self, queryset, name, value):
        return queryset.annotate(dobviolations=Count('dobviolation', distinct=True)).filter(dobviolations__lte=value)

    # ECBViolations
    def filter_ecbviolations_exact(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations=value)

    def filter_ecbviolations_gt(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gt=value)

    def filter_ecbviolations_gte(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__gte=value)

    def filter_ecbviolations_lt(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lt=value)

    def filter_ecbviolations_lte(self, queryset, name, value):
        return queryset.annotate(ecbviolations=Count('ecbviolation', distinct=True)).filter(ecbviolations__lte=value)

    class Meta:
        model = ds.Property
        fields = {
            'yearbuilt': ['exact', 'lt', 'gt', 'gte', 'lte'],
            'council': ['exact']

        }
