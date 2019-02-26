from datasets import models as ds
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField
from django.db.models.functions import Cast

import re


def annotate_rentstabilized(queryset, c_filter):
    rsvalues = c_filter['query1_filters']

    start_year = [*rsvalues[0].keys()][0].split('__', 2)[1].split('uc', 1)[1]
    end_year = [*rsvalues[1].keys()][0].split('__', 2)[1].split('uc', 1)[1]
    queryset = queryset.annotate(**{'rentstabilizationrecord' + start_year: F('rentstabilizationrecord__uc' + start_year)}).annotate(**{
        'rentstabilizationrecord' + end_year: F('rentstabilizationrecord__uc' + end_year)})
    queryset = queryset.annotate(
        rentstabilizationrecords__percent=ExpressionWrapper(
            1 - Cast(F('rentstabilizationrecord' + end_year), FloatField()) /
            Cast(F('rentstabilizationrecord' + start_year), FloatField()), output_field=FloatField()
        )
    )
    return queryset


def clean_model_name(string):
    return string[:-1] if string.endswith('s') else string


def get_annotation_key(string):
    # returns entire ,.*__count filter string minus the comparison
    for filter in string.split(','):
        if 'count' in filter.lower() or 'percent' in filter.lower():
            filter = re.sub(r"(__gte\b|__gt\b|__exact\b|__lt\b|__lte\b|)", '', filter.split('=')[0])
            return filter


def get_filters(string, annotation=False):
    filter_strings = list(
        filter(lambda x: bool(re.search(r"(count|percent)", x.lower())) == annotation, string.split(',')))

    if not annotation:
        # convert the date fields to singular model names
        filter_strings = list(map(lambda x: "__".join(
            [clean_model_name(x.split('__', 1)[0]), x.split('__', 1)[1]]), filter_strings))
    return list(map(lambda x: {x.split('=')[0]: x.split('=')[1]}, filter_strings))


def parse_filter_string(string):
    if re.search(r'\bAND\b', string.upper()):
        return None
    if re.search(r'\bOR\b', string.upper()):
        return None
    if 'CONDITION' in string.upper():
        return {'condition': int(string.split('=')[1].split('_')[1])}

    model = clean_model_name(string.lower().split('=', 1)[1].split('__')[0])

    return {
        'model': model,
        'prefetch_key': model + '_set',
        'annotation_key': get_annotation_key(string),
        'query1_filters': get_filters(string.split('=', 1)[1], annotation=False),
        'query2_filters': get_filters(string.split('=', 1)[1], annotation=True)

    }


def convert_query_string_to_mapping(string):
    # Converts query string:
    # *condition_0=AND+filter_0=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10
    # into:
    # [
    #   {'type': 'AND',
    #    'filters': [
    #       {condition: 1}, (if condition)
    #       {
    #         'model': 'hpdviolation',
    #         'prefetch_key': 'hpdviolation_set',
    #         'annotation_key': 'hpdviolations__count',
    #         'query1_filters': ['hpdviolation__approveddate__gte': '2018-01-01']
    #         'query2_filters': ['hpdviolations__count__gte': '10']
    #       }
    #     ]
    #   }
    # ]
    conditions = []
    array = string.split('*')
    array = list(filter(None, array))
    for condition in array:
        element = {
            'type': condition.split('=', 1)[1].split(' ')[0],
            'filters': list(filter(None, list(map(lambda x: parse_filter_string(x),  list(filter(None, condition.split(' ')))))))
        }
        conditions.append(element)

    return conditions


def construct_or_q(query_list):
    ql = query_list[:]
    query = Q(**ql.pop())

    if len(ql):
        for item in ql:
            query |= Q(**item)

    return query


def construct_and_q(query_list):
    ql = query_list[:]
    query = Q(**ql.pop())

    if len(ql):
        for item in ql:
            query &= Q(**item)

    return query


def convert_condition_to_q(condition, conditions, type='query1_filters'):
    # only seed condition0, let it recurisvely construct rest of Q
    q = Q()
    if condition['type'].lower() == 'and':
        for c_filter in condition['filters']:
            if 'condition' in c_filter:
                q &= convert_condition_to_q(conditions[c_filter['condition']], conditions, type)
            else:
                if type == 'query2_filters' and c_filter['annotation_key']:
                    q &= construct_and_q(c_filter[type])
                elif type == 'query1_filters':
                    q |= construct_and_q(c_filter[type])
    elif condition['type'].lower() == 'or':
        for c_filter in condition['filters']:
            if 'condition' in c_filter:
                q |= convert_condition_to_q(conditions[c_filter['condition']], conditions, type)
            else:
                if type == 'query2_filters' and c_filter['annotation_key']:
                    q |= construct_and_q(c_filter[type])
                elif type == 'query1_filters':
                    q |= construct_and_q(c_filter[type])
    return q
