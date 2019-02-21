from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class EvictionViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.eviction_factory(courtindexnumber="1")
        self.eviction_factory(courtindexnumber="2")

        response = self.client.get('/evictions/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        eviction = self.eviction_factory(courtindexnumber="1")

        response = self.client.get('/evictions/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["courtindexnumber"], '1')
