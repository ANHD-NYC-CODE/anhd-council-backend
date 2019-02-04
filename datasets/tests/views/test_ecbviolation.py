from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class ECBViolationViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.ecbviolation_factory(ecbviolationnumber="1")
        self.ecbviolation_factory(ecbviolationnumber="2")

        response = self.client.get('/ecbviolations/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.ecbviolation_factory(ecbviolationnumber="1")

        response = self.client.get('/ecbviolations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["ecbviolationnumber"], '1')
