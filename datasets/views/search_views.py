from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds
from django.contrib.postgres.search import SearchVector
from django.db.models import Q, F
from django.contrib.postgres.search import SearchQuery, SearchRank
from datasets.filter_helpers import construct_or_q, construct_and_q


class SearchViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    def building_search(self, request, *args, **kwargs):
        self.serializer_class = serial.BuildingSearchSerializer

        search_term = None
        if 'fts' in request.query_params:
            search_term = request.query_params['fts'].replace(',', '')
            # terms = []
            # for term in list(search_term.split(' ')):
            #     terms.append(SearchQuery(term + ':*'))
            #
            # queries = construct_and_q(terms)

            #
            # self.queryset = ds.AddressRecord.objects.annotate(rank=SearchRank(F('address'), queries)).filter(
            #     address=queries, rank__gte=0).order_by('-rank')[:5]

            # https://czep.net/17/full-text-search.html

            STREET_ABBREVIATIONS = ('ln', 'pl', 'dr', 'rd', 'st', 'ave', 'blvd')

            ##
            # Transforms
            # 100 grand st
            # to
            # 100:* | grand:* | st:*
            terms = search_term.split(' ')
            if len(terms) <= 1:
                terms = ':*'.join(terms)
            else:
                first_term = terms.pop(0) + ' & '
                terms = first_term + ':* & '.join(terms)
                terms = terms + ':*'

            rank_normalization = 1
            rank_field = 'rank'
            vector_column = '"datasets_addressrecord"."address"'
            ts_query = "(to_tsquery('%s'))" % terms
            where_q = "\"datasets_addressrecord\".\"address\" @@ %s" % (ts_query + '= true')
            select = {}
            select[rank_field] = 'ts_rank( "datasets_addressrecord"."address", %s, %d )' % (
                ts_query, rank_normalization)
            order = ['-%s' % rank_field]

            # bins_list = [doc['bin'] for doc in ds.AddressRecord.objects.extra(
            #     select=select, where=[where_q], order_by=order
            # )[:5].values('bin')]

            # self.queryset = ds.Building.objects.filter(bin__in=bins_list).all()
            self.queryset = ds.AddressRecord.objects.extra(
                select=select, where=[where_q], order_by=order
            )[:5]

        else:
            self.queryset = ds.Building.objects.all().order_by('pk')
        return super().list(request, *args, **kwargs)
