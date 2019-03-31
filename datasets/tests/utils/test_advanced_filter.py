from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest
from django.db.models import Q

from datasets.utils import advanced_filter as af
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyFilterTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_convert_query_string_to_mapping_1(self):
        query_string = "*condition_0=AND filter_0=condition_1 filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__approveddate__lte=2019-01-01,hpdviolations__count__gte=10 *condition_1=OR filter_0=dobviolations__issueddate__gte=2018-01-01,dobviolations__count__gte=10 filter_1=ecbviolations__issueddate__gte=2018-01-01,ecbviolations__count__gte=10"

        result = af.convert_query_string_to_mapping(query_string)
        expected = {'0':
                    {'id': '0', 'type': 'AND',
                     'filters': [
                         {'condition': '1'},
                         {
                             'model': 'hpdviolation',
                             'related_annotation_key': 'filter_0_hpdviolation_set',
                             'count_annotation_key': 'filter_0_hpdviolations__count',
                             'query1_filters': [{'hpdviolation__approveddate__gte': '2018-01-01'}, {'hpdviolation__approveddate__lte': '2019-01-01'}],
                             'query2_filters': [{'filter_0_hpdviolations__count__gte': '10'}]
                         }
                     ]
                     },
                    '1':
                    {'type': 'OR',
                        'filters': [
                            {
                                'model': 'dobviolation',
                                'related_annotation_key': 'filter_0_dobviolation_set',
                                'count_annotation_key': 'filter_0_dobviolations__count',
                                'query1_filters': [{'dobviolation__issueddate__gte': '2018-01-01'}],
                                'query2_filters': [{'filter_0_dobviolations__count__gte': '10'}]
                            },
                            {
                                'model': 'ecbviolation',
                                'related_annotation_key': 'filter_1_ecbviolation_set',
                                'count_annotation_key': 'filter_1_ecbviolations__count',
                                'query1_filters': [{'ecbviolation__issueddate__gte': '2018-01-01'}],
                                'query2_filters': [{'filter_1_ecbviolations__count__gte': '10'}]
                            }
                        ]
                     }
                    }
        self.assertEqual(result['0']['type'], expected['0']['type'])
        self.assertEqual(result['1']['type'], expected['1']['type'])
        self.assertEqual(result['0']['filters'][0], expected['0']['filters'][0])
        self.assertEqual(result['1']['filters'][1]['model'], expected['1']['filters'][1]['model'])
        self.assertEqual(result['1']['filters'][1]['related_annotation_key'],
                         expected['1']['filters'][1]['related_annotation_key'])
        self.assertEqual(result['1']['filters'][1]['count_annotation_key'],
                         expected['1']['filters'][1]['count_annotation_key'])
        self.assertEqual(result['1']['filters'][1]['query1_filters'], expected['1']['filters'][1]['query1_filters'])
        self.assertEqual(result['1']['filters'][1]['query2_filters'], expected['1']['filters'][1]['query2_filters'])

    def test_convert_condition_to_q(self):
        # hpdviolations and either dobviolations or ecbviolations
        # with query1_filters
        query_string = "*condition_0=AND filter_0=condition_1 filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10 *condition_1=OR filter_0=dobviolations__issueddate__gte=2018-01-01,dobviolations__count__gte=10 filter_1=ecbviolations__issueddate__gte=2018-01-01,ecbviolations__count__gte=10"
        mapping = af.convert_query_string_to_mapping(query_string)
        result = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query1_filters')
        expected = Q((Q(('dobviolation__issueddate__gte', '2018-01-01')) |
                      Q(('ecbviolation__issueddate__gte', '2018-01-01'))), ('hpdviolation__approveddate__gte', '2018-01-01'))

        self.assertEqual(result, expected)

        # With query2_filters

        result2 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query2_filters')
        expected2 = Q((Q(('filter_0_dobviolations__count__gte', '10')) |
                       Q(('filter_1_ecbviolations__count__gte', '10'))), ('filter_1_hpdviolations__count__gte', '10'))

        self.assertEqual(result2, expected2)
