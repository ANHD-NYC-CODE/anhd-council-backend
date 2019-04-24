from django.db.models import FieldDoesNotExist
from datasets import models as ds
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField, Prefetch, FilteredRelation, OuterRef, Exists
from django.db.models.functions import Cast
from django.conf import settings
from rest_framework.exceptions import APIException

import re
import collections


def annotate_dataset(queryset, c_filter, bbl_values):
    model_name = list(filter(lambda x: c_filter['model'].lower() == x.lower(), settings.ACTIVE_MODELS))
    model = getattr(ds, model_name[0])

    queryset = queryset.annotate(
        **{c_filter['related_annotation_key']: FilteredRelation(c_filter['model'], condition=Q(construct_and_q(c_filter['query1_filters']), Q(**{c_filter['model'] + '__bbl__in': bbl_values})))})

    if c_filter['count_annotation_key']:
        queryset = queryset.annotate(**{c_filter['count_annotation_key']
                                     : Count(c_filter['related_annotation_key'], distinct=True)})

    return queryset


def annotate_acrislegals(queryset, c_filter, bbl_values):

    # clean filters, since the advanced search typically tacks on the property field
    # but we need the acrisrealmaster field since we're going to be doing a subquery on it
    cleaned_filters = []
    for f in c_filter['query1_filters']:
        for key in f.keys():
            cleaned_filters.append({key.replace('acrisreallegal__documentid__', ''): f[key]})

    masterdocid_values = ds.AcrisRealMaster.construct_sales_query('acrisreallegal__documentid').only('documentid')
    masterdocid_values = masterdocid_values.filter(construct_and_q(cleaned_filters)).values('documentid')

    # filteredRelation for acrislegals where master conditions and bbl conditions match
    queryset = queryset.annotate(
        **{c_filter['related_annotation_key']: FilteredRelation(c_filter['model'], condition=Q(Q(**{c_filter['model'] + '__documentid__in': masterdocid_values}), Q(**{c_filter['model'] + '__bbl__in': bbl_values})))})

    if c_filter['count_annotation_key']:

        if '{}_acrisreallegals__documentid__docamount'.format(c_filter['filter_id']) in c_filter['count_annotation_key']:
            # annotate on value of docamount column from acrisreallegal_set* filtered relation
            queryset = queryset.annotate(
                **{c_filter['count_annotation_key']: F('acrisreallegal_set__{}__documentid__docamount'.format(c_filter['filter_id']))})

        else:
            # annotate on count of acris records

            queryset = queryset.annotate(**{c_filter['count_annotation_key']                                            : Count(c_filter['related_annotation_key'], distinct=True)})
    return queryset


def annotate_rentstabilized(queryset, c_filter):
    rsvalues = c_filter['query1_filters']

    start_year = [*rsvalues[0].keys()][0].split('__', 2)[1].split('uc', 1)[1]
    end_year = [*rsvalues[1].keys()][0].split('__', 2)[1].split('uc', 1)[1]

    start_annotation = '{}_rentstabilizationrecord{}'.format(c_filter['filter_id'], start_year)
    end_annotation = '{}_rentstabilizationrecord{}'.format(c_filter['filter_id'], end_year)

    queryset = queryset.annotate(**{start_annotation: F('rentstabilizationrecord__uc' + start_year)}).annotate(**{
        '{}_rentstabilizationrecord{}'.format(c_filter['filter_id'], end_year): F('rentstabilizationrecord__uc' + end_year)})

    queryset = queryset.annotate(
        **{'{}_rentstabilizationrecords__percent'.format(c_filter['filter_id']): ExpressionWrapper(
            1 - Cast(F(end_annotation), FloatField()) /
            Cast(F(start_annotation), FloatField()), output_field=FloatField()
        )}
    )

    return queryset


def clean_model_name(string):
    return string[:-1] if string.endswith('s') else string


def get_count_annotation_key(string, filter_id):
    new_string = re.sub(r"(?=filter)(.*?)(?=\=)", '', string)
    # returns entire ,.*__count filter string minus the comparison
    for filter in new_string.split(','):
        if bool(re.search(r"(count|percent)", filter.lower())):
            filter = re.sub(r"(__gte\b|__gt\b|__exact\b|__lt\b|__lte\b|)", '', filter.split('=')[0])
            return "{}_{}".format(filter_id, filter)


def get_filters(string, filter_id, annotation=False):
    filter_strings = list(
        filter(lambda x: bool(re.search(r"(count|percent)", x.lower())) == annotation, string.split(',')))

    if annotation:
        dup = []
        for str in filter_strings:

            str = str.split('_')
            str.insert(0, filter_id)
            str = '_'.join(str)
            dup.append(str)

        filter_strings = dup
    else:
        # convert the date fields to singular model names
        filter_strings = list(map(lambda x: "__".join(
            [clean_model_name(x.split('__', 1)[0]), x.split('__', 1)[1]]), filter_strings))

        # RentstabilizationRecord special string
        # converts "rentstabilizationrecords__year__gte=2007"
        # into "rentstabilizationrecord__uc2017__gt=0"
        if 'rentstabilizationrecord' in string:
            filter_strings = list(map(lambda x: "__".join(
                [clean_model_name(x.split('__', 1)[0]) + '__uc' + x.split('=', 1)[1] + '__gt=0']), filter_strings))

    return list(map(lambda x: {x.split('=')[0]: x.split('=')[1]}, filter_strings))


def parse_filter_string(string):
    tokens = string.split('=', 1)

    if 'CONDITION' in tokens[0].upper():
        # don't parse conditions
        return None
    if 'CONDITION' in tokens[1].upper():
        # Do parse filter conditions
        # and return the condition filter mapping

        return {'condition': tokens[1].split('_')[1]}

    filter_id = tokens[0]
    filter_value = tokens[1]
    if not filter_value:
        return None

    model = clean_model_name(tokens[1].split('__')[0])

    mapping = {
        'model': model,
        'related_annotation_key': filter_id + '_' + model + '_set',
        'filter_id': filter_id,
        'count_annotation_key': get_count_annotation_key(string.split('=', 1)[1], filter_id),
        'query1_filters': get_filters(string.split('=', 1)[1], filter_id, annotation=False),
        'query2_filters': get_filters(string.split('=', 1)[1], filter_id, annotation=True)
    }

    # if no count, add a default gte=1 count
    if not mapping['count_annotation_key']:
        mapping['count_annotation_key'] = '{}__count'.format(filter_id)
        mapping['query2_filters'] = [{'{}__count__gte'.format(filter_id): 1}]

    return mapping


def validate_mapping(request, mapping):
    for condition_key in mapping.keys():
        if not re.search(r"(\bAND\b|\bOR\b)", mapping[condition_key]['type']):
            raise APIException("\"{}\" is not a valid condition type. use only AND or OR".format(
                mapping[condition_key]['type']))
        if not len(mapping[condition_key]['filters']):
            raise APIException("Condition {} has no filters".format(condition_key))
        for c_filter in mapping[condition_key]['filters']:
            if 'model' in c_filter:
                model_name = list(filter(lambda x: c_filter['model'].lower() == x.lower(), settings.ACTIVE_MODELS))
                if not model_name:
                    # Validate model names
                    raise APIException(
                        "\"{}\" is not a valid dataset. Was it spelled correctly?".format(c_filter['model']))
                else:
                    # valid model fields
                    model = getattr(ds, model_name[0])

                    for fil in c_filter['query1_filters']:
                        for key in fil.keys():
                            key_split = key.split('__')
                            # remove dataset and comparison from front and end
                            key_split.pop(0)
                            if (len(key_split) >= 2):
                                key_split.pop()
                            # only valid on first field, can't validate here on related fields
                            field = key_split[0]
                            try:
                                model._meta.get_field(field)
                            except FieldDoesNotExist:
                                raise APIException(
                                    "Field \"{}\" is not valid for dataset \"{}\"".format(field, model.__name__))


def convert_query_string_to_mapping(string):
    # Converts query string:
    # *condition_0=AND filter_0=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10
    # into:
    # [
    #   {'type': 'AND',
    #    'filters': [
    #       {condition: 1}, (if condition)
    #       {
    #         'model': 'hpdviolation',
    #         'related_annotation_key': 'hpdviolation_set',
    #         'count_annotation_key': 'hpdviolations__count',
    #         'query1_filters': ['hpdviolation__approveddate__gte': '2018-01-01']
    #         'query2_filters': ['hpdviolations__count__gte': '10']
    #       }
    #     ]
    #   }
    # ]
    conditions = collections.OrderedDict()
    array = string.split('*')
    array = list(filter(None, array))
    for con in array:
        try:
            type = con.split('=', 1)[1].split(' ')[0]
        except APIException as e:
            type = None

        element = {
            'id': con.split('=', 1)[0].split('_')[1],
            'type': type,
            'filters': list(filter(None, list(map(lambda x: parse_filter_string(x),  list(filter(None, con.split(' ')))))))
        }
        conditions[element['id']] = element

    return conditions


def construct_or_q(query_list):
    ql = query_list[:]
    if (len(ql)):
        query = Q(**ql.pop())
    else:
        query = Q()

    if len(ql):
        for item in ql:
            query |= Q(**item)

    return query


def construct_and_q(query_list):

    ql = query_list[:]
    if (len(ql)):
        query = Q(**ql.pop())
    else:
        query = Q()

    if len(ql):
        for item in ql:
            query &= Q(**item)

    return query


def convert_condition_to_q(condition_key, mapping, filter_pass='query1_filters'):
    # only seed condition0 in view-filter, let it recurisvely construct rest of Q
    q = Q()

    if mapping[condition_key]['type'].upper() == 'AND':
        for c_filter in mapping[condition_key]['filters']:
            if 'condition' in c_filter:

                q &= convert_condition_to_q(c_filter['condition'], mapping, filter_pass)
            else:
                if filter_pass == 'query2_filters' and c_filter['count_annotation_key']:
                    q &= construct_and_q(c_filter[filter_pass])
                elif filter_pass == 'query1_filters':
                    q &= construct_and_q(c_filter[filter_pass])
    elif mapping[condition_key]['type'].upper() == 'OR':
        for c_filter in mapping[condition_key]['filters']:
            if 'condition' in c_filter:
                q |= convert_condition_to_q(c_filter['condition'], mapping, filter_pass)
            else:
                if filter_pass == 'query2_filters' and c_filter['count_annotation_key']:
                    q |= construct_and_q(c_filter[filter_pass])
                elif filter_pass == 'query1_filters':
                    q |= construct_and_q(c_filter[filter_pass])
    return q
