from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class Subsidy421aTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.subsidy421a_factory()
        self.subsidy421a_factory()

        response = self.client.get('/subsidy421a/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        subsidy421a = self.subsidy421a_factory()

        response = self.client.get('/subsidy421a/{}/'.format(subsidy421a.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], subsidy421a.id)
