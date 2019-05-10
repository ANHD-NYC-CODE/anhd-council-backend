from datasets import models as ds
import rest_framework_filters as filters
import django_filters
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField, Case, When, Value
from datasets.utils import advanced_filter as af

from datasets.filter_helpers import PercentWithDateField, AdvancedQueryFilter, CommaSeparatedConditionField
from django.db.models import Q

from datasets.filters.PropertyFilter import housingtype_filter, rsunits_filter, programnames_filter
import logging

logger = logging.getLogger('app')


class AdvancedPropertyFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        return super(AdvancedPropertyFilter, self).__init__(*args, **kwargs)

    @property
    def qs(self):
        return super(AdvancedPropertyFilter, self).qs

    q = AdvancedQueryFilter(method='filter_advancedquery')

    def filter_advancedquery(self, queryset, name, values):
        # Turns out the queryset that comes here is not guaranteed to be pre-filled with
        # council or housing type filters / subqueries

        # Need to override the queryset to ensure subqueries come before joins
        bbl_queryset = ds.Property.objects
        params = dict(self.request.query_params)

        # converts the param values into an array for some reason...
        del params['q']
        params.pop('summary', None)
        params.pop('summary-type', None)
        if 'format' in params:
            del params['format']
        if 'council' in params:
            bbl_queryset = bbl_queryset.filter(bbl__in=bbl_queryset.council(params['council'][0]).values('bbl'))
            del params['council']
        elif 'community' in params:
            bbl_queryset = bbl_queryset.filter(bbl__in=bbl_queryset.community(params['community'][0]).values('bbl'))
            del params['community']
        if 'housingtype' in params:
            bbl_queryset = bbl_queryset.filter(bbl__in=housingtype_filter(
                self, bbl_queryset, name, params['housingtype'][0]).values('bbl'))
            del params['housingtype']
        if 'rsunitslost__start' in params:
            start = params['rsunitslost__start'][0]
            del params['rsunitslost__start']
            end = None
            lt = None
            lte = None
            exact = None
            gt = None
            gte = None
            if 'rsunitslost__end' in params:
                end = params['rsunitslost__end'][0]
                del params['rsunitslost__end']
            if 'rsunitslost__lt' in params:
                lt = params['rsunitslost__lt'][0]
                del params['rsunitslost__lt']
            if 'rsunitslost__lte' in params:
                lte = params['rsunitslost__lte'][0]
                del params['rsunitslost__lte']
            if 'rsunitslost__exact' in params:
                exact = params['rsunitslost__exact'][0]
                del params['rsunitslost__exact']
            if 'rsunitslost__gt' in params:
                gt = params['rsunitslost__gt'][0]
                del params['rsunitslost__gt']
            if 'rsunitslost__gte' in params:
                gte = params['rsunitslost__gte'][0]
                del params['rsunitslost__gte']

            rsunitslost_params = (start,
                                  end,
                                  lt,
                                  lte,
                                  exact,
                                  gt,
                                  gte,)

            bbl_queryset = bbl_queryset.filter(bbl__in=rsunits_filter(self,
                                                                      bbl_queryset, name, PercentWithDateField.compress(self, rsunitslost_params)))

        if 'coresubsidyrecord__programname__any' in params:
            programname_params = (params['coresubsidyrecord__programname__any'][0], None, None, None)

            bbl_queryset = bbl_queryset.filter(bbl__in=programnames_filter(
                self, bbl_queryset, 'propertyannotation__subsidyprograms', CommaSeparatedConditionField.compress(self, programname_params)))
        # add all the other params
        for key, value in params.items():
            try:
                bbl_queryset = bbl_queryset.filter(**{key: value[0]})
            except Exception as e:
                print("AdvancedFilter processed a non-property field: {}".format(e))
                logger.debug("AdvancedFilter processed a non-property field: {}".format(e))

        # finally, construct subquery

        bbl_queryset = bbl_queryset.filter(bbl__in=queryset.only('bbl'))

        # NOW parse the q advanced query
        mapping = af.convert_query_string_to_mapping(values)

        af.validate_mapping(self.request, mapping)

        for con in mapping.keys():
            for c_filter in mapping[con]['filters']:
                if 'condition' in c_filter:
                    # skip condition filters
                    continue

                if c_filter['model'] == 'rentstabilizationrecord':
                    queryset = af.annotate_rentstabilized(queryset, c_filter)
                elif c_filter['model'].lower() == 'acrisreallegal':
                    queryset = af.annotate_acrislegals(queryset, c_filter, bbl_queryset.values('bbl'))

                else:
                    queryset = af.annotate_dataset(queryset, c_filter, bbl_queryset.values('bbl'))

        # q1 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query1_filters')
        # q1_queryset = queryset.filter(q1)

        # filter on annotating filters (like counts)

        # q1 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query1_filters')
        q2 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query2_filters')

        queryset = queryset.filter(q2, bbl__in=bbl_queryset.values('bbl'))
        # q2_queryset = q1_queryset.filter(q2)
        #
        # final_bbls = q2_queryset.values('bbl')

        return queryset
