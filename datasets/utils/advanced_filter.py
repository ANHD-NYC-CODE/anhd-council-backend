from datasets import models as ds
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField
import re


def clean_model_name(string):
    return string[:-1] if string.endswith('s') else string


def get_annotation_key(string):
    pattern = r"(?=count|percent|amount)(.*?)(?=__(gte|lte|exact|lt|gt))"
    match = re.search(pattern, string.lower())
    if match:
        return match.group()
    else:
        raise Exception('No annotation key present in string: {}'.format(string))


def get_filters(string, annotation=False):
    filter_strings = list(
        filter(lambda x: bool(re.search(r"(count|amount|percent)", x.lower())) == annotation, string.split(',')))

    if not annotation:
        # convert the date fields to singular model names
        filter_strings = list(map(lambda x: "__".join(
            [clean_model_name(x.split('__', 1)[0]), x.split('__', 1)[1]]), filter_strings))
    return list(map(lambda x: {x.split('=')[0]: x.split('=')[1]}, filter_strings))


def parse_filter_string(string):
    if 'AND' in string.upper():
        return None
    if 'OR' in string.upper():
        return None
    if 'CONDITION' in string.upper():
        return {'condition': int(string.split('=')[1].split('_')[1])}

    model = clean_model_name(string.lower().split('=', 1)[1].split('__')[0])
    return {
        'model': model,
        'prefetch_key': model + '_set',
        'annotation_key': model + 's__' + get_annotation_key(string),
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
            'type': condition.split('=', 1)[1].split('+')[0],
            'filters': list(filter(None, list(map(lambda x: parse_filter_string(x),  list(filter(None, condition.split('+')))))))
        }
        conditions.append(element)

    return conditions


def convert_condition_to_q():
    import pdb
    pdb.set_trace()
