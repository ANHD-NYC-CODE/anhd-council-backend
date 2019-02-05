from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds
from django.contrib.postgres.search import SearchVector
from django.db.models import Q


class SearchViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    def building_search(self, request, *args, **kwargs):
        search_term = None
        if 'fts' in request.query_params:
            search_term = request.query_params['fts']
            self.queryset = ds.Building.objects.filter(address_search=search_term).only(
                'bin', 'bbl', 'lhnd', 'hhnd', 'stname', 'boro', 'zipcode').all().order_by('pk')
            # split_search = search_term.split(' ')
            # if (len(split_search) <= 1):
            #     house_number = search_term
            #     street_name = search_term
            #     self.queryset = ds.Building.objects.filter(Q(low_search=house_number) | Q(
            #         high_search=house_number) | Q(street_search=street_name)).all().order_by('pk')
            # elif len(split_search) > 1:
            #     house_number = split_search[0]
            #     street_name = split_search[1]
            #     self.queryset = ds.Building.objects.filter(
            #         Q(low_search=house_number) | Q(high_search=house_number), street_search=street_name).all().order_by('pk')
        else:
            self.queryset = ds.Building.objects.all().order_by('pk')
        self.serializer_class = serial.BuildingSearchSerializer
        return super().list(request, *args, **kwargs)
