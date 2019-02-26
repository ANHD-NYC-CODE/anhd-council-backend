from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets.utils import advanced_filter as af
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyFilterTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_convert_query_string_to_mapping_1(self):
        query_string = "*condition_0=AND+filter_0=condition_1+filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10+*condition_1=OR+filter_0=dobviolations__issueddate__gte=2018-01-01,dobviolations__count__gte=10+filter_1=ecbviolations__issueddate__gte=2018-01-01,ecbviolations__count__gte=10"

        result = af.convert_query_string_to_mapping(query_string)
        expected = [
            {'type': 'AND',
             'filters': [
                 {'condition': 1},
                 {
                     'model': 'hpdviolation',
                     'prefetch_key': 'hpdviolation_set',
                     'annotation_key': 'hpdviolations__count',
                     'query1_filters': [{'hpdviolation__approveddate__gte': '2018-01-01'}],
                     'query2_filters': [{'hpdviolations__count__gte': '10'}]
                 }
             ]
             },
            {'type': 'OR',
             'filters': [
                 {
                     'model': 'dobviolation',
                     'prefetch_key': 'dobviolation_set',
                     'annotation_key': 'dobviolations__count',
                     'query1_filters': [{'dobviolation__issueddate__gte': '2018-01-01'}],
                     'query2_filters': [{'dobviolations__count__gte': '10'}]
                 },
                 {
                     'model': 'ecbviolation',
                     'prefetch_key': 'ecbviolation_set',
                     'annotation_key': 'ecbviolations__count',
                     'query1_filters': [{'ecbviolation__issueddate__gte': '2018-01-01'}],
                     'query2_filters': [{'ecbviolations__count__gte': '10'}]
                 }
             ]
             }
        ]
        self.assertEqual(result[0]['type'], expected[0]['type'])
        self.assertEqual(result[1]['type'], expected[1]['type'])
        self.assertEqual(result[0]['filters'][0], expected[0]['filters'][0])
        self.assertEqual(result[1]['filters'][1]['model'], expected[1]['filters'][1]['model'])
        self.assertEqual(result[1]['filters'][1]['prefetch_key'], expected[1]['filters'][1]['prefetch_key'])
        self.assertEqual(result[1]['filters'][1]['annotation_key'], expected[1]['filters'][1]['annotation_key'])
        self.assertEqual(result[1]['filters'][1]['query1_filters'], expected[1]['filters'][1]['query1_filters'])
        self.assertEqual(result[1]['filters'][1]['query2_filters'], expected[1]['filters'][1]['query2_filters'])
