from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds
from django.contrib.postgres.search import SearchVector
from django.db.models import Q, F
from django.contrib.postgres.search import SearchQuery, SearchRank
from datasets.filter_helpers import construct_or_q, construct_and_q
from rest_framework.permissions import IsAuthenticated


class SearchViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def building_search(self, request, *args, **kwargs):
        self.serializer_class = serial.BuildingSearchSerializer
        self.pagination_class = None

        search_term = None
        if 'fts' in request.query_params:
            search_term = request.query_params['fts'].replace(',', '').strip()

            def construct_search_query(search_term, prefix_first=False):
                split_terms = search_term.split(' ')

                ##
                # Transforms
                # 100 grand st
                # to
                # 100:* | grand:* | st:*
                if len(split_terms) <= 1:
                    terms = ':*'.join(split_terms)
                else:
                    first_term = split_terms.pop(0)
                    if prefix_first:
                        terms = ':* & '.join([first_term] + split_terms)
                        terms = terms + ':*'
                    else:
                        terms = first_term + ' & ' + ':* & '.join(split_terms)
                        terms = terms + ':*'

                # https://czep.net/17/full-text-search.html
                rank_normalization = 16 if prefix_first else 32
                rank_field = 'rank'
                vector_column = '"datasets_addressrecord"."address"'
                ts_query = "(to_tsquery('%s'))" % terms
                where_q = "\"datasets_addressrecord\".\"address\" @@ %s" % (ts_query + '= true')
                select = {}
                select[rank_field] = 'ts_rank( "datasets_addressrecord"."address", %s, %d )' % (
                    ts_query, rank_normalization)
                order = ['-%s' % rank_field]

                return ds.AddressRecord.objects.extra(
                    select=select, where=[where_q], order_by=order
                )[:4]

                # return ds.Building.objects.filter(bin__in=bins).annotate(rank=bins['rank'])

            qs = construct_search_query(search_term, True).union(
                construct_search_query(search_term, False)).order_by('-rank')[:4]
            keys = list(doc.key for doc in qs)
            self.queryset = ds.AddressRecord.objects.filter(key__in=keys).distinct('bin')

        else:
            self.queryset = ds.Building.objects.all().order_by('pk')
        return super().list(request, *args, **kwargs)
