from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class HPDViolationViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdviolation_factory(violationid="1")
        self.hpdviolation_factory(violationid="2")

        response = self.client.get('/hpdviolations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.hpdviolation_factory(violationid="1")

        response = self.client.get('/hpdviolations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["violationid"], 1)
