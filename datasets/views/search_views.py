from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet

from datasets import serializers as serial
from datasets import models as ds
from django.contrib.postgres.search import SearchVector
from django.db.models import Q, F, Case, When
from django.contrib.postgres.search import SearchQuery, SearchRank
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger('app')


class SearchViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    # permission_classes = (IsAuthenticated,)

    def building_search(self, request, *args, **kwargs):
        self.serializer_class = serial.BuildingSearchSerializer
        self.pagination_class = None
        search_term = None

        def construct_search_terms(terms, token, add_star=False, add_ampersand=False):
            def star(add_star=False):
                if add_star:
                    return ':*'
                else:
                    return ''

            def ampersand(add_ampersand=False):
                if add_ampersand:
                    return ' & '
                else:
                    return ''

            terms = terms + token + star(add_star) + ampersand(add_ampersand)

            return terms

        if 'fts' in request.query_params:
            search_term = request.query_params['fts'].replace(',', '').strip()

            def construct_search_query(search_term, prefix_first=False):
                tokens = search_term.strip().split(' ')
                terms = ''

                ##
                # Transforms
                # 100 grand st
                # to
                # 100:* | grand:* | st:*
                if len(tokens) <= 1:
                    terms = ':*'.join(tokens)
                else:
                    if prefix_first:
                        for i in range(len(tokens)):
                            if i == len(tokens) - 1 and len(tokens[i]) <= 1:
                                # on last token if token is <= 1 chars, don't add star, don't add ampersand
                                terms = construct_search_terms(terms, tokens[i], False, False)
                            elif i == len(tokens) - 1:
                                # on last token don't add ampersand
                                terms = construct_search_terms(terms, tokens[i], True, False)
                            else:
                                terms = construct_search_terms(terms, tokens[i], True, True)
                    else:
                        for i in range(len(tokens)):
                            if i == 0:
                                # first token, don't use * star
                                terms = construct_search_terms(terms, tokens[i], False, True)
                            elif i == len(tokens) - 1 and len(tokens[i]) <= 1:
                                # on last token if token is <= 1 chars, don't add star, don't add ampersand
                                terms = construct_search_terms(terms, tokens[i], False, False)
                            elif i == len(tokens) - 1:
                                # on last token don't add ampersand
                                terms = construct_search_terms(terms, tokens[i], True, False)
                            else:
                                terms = construct_search_terms(terms, tokens[i], True, True)

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
                ).order_by('-rank')[:4]

            # returns results mixed with 2 queries -
            # 1: does not include :* on the first token only`
            # 2: includes :* prefix on all tokens
            qs = construct_search_query(search_term, False).union(
                construct_search_query(search_term, True)).order_by('-rank').values('key', 'rank')

            keys_list = list(doc['key'] for doc in qs)

            # Preserves order of keys_list in final query
            preserved = Case(*[When(key=key, then=pos) for pos, key in enumerate(keys_list)])

            self.queryset = ds.AddressRecord.objects.filter(key__in=keys_list).order_by(preserved)

        else:
            self.queryset = ds.Building.objects.all().order_by('pk')
        return super().list(request, *args, **kwargs)
