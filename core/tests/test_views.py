from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from users import views as v
import logging
logging.disable(logging.CRITICAL)


class DatasetViews(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_get_datasets(self):
        dataset = self.dataset_factory(name="Property")
        dataset2 = self.dataset_factory(name="Foreclosure")
        dataset3 = self.dataset_factory(name="PSPreForeclosure")
        update = self.update_factory(dataset=dataset, completed_date="2018-01-01")
        update2 = self.update_factory(dataset=dataset3, completed_date="2018-01-01")
        datafile = self.datafile_factory(dataset=dataset, version="18")

        response = self.client.get('/datasets/?format=json')

        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content[0]['version'], "18")
        self.assertEqual(content[0]['last_update'].year, 2018)
        self.assertEqual(content[1]['last_update'].year, 2018)
