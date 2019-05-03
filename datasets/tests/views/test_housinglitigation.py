from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class HousingLitigationViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.housinglitigation_factory(litigationid="1")
        self.housinglitigation_factory(litigationid="2")

        response = self.client.get('/housinglitigations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        housinglitigation = self.housinglitigation_factory(litigationid="1")

        response = self.client.get('/housinglitigations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["litigationid"], 1)
