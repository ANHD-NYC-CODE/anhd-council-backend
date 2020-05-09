from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class AEPBuildingViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.aepbuilding_factory()
        self.aepbuilding_factory()

        response = self.client.get('/aepbuildings/', format="json")

        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.aepbuilding_factory(id='1')

        response = self.client.get('/aepbuildings/1/')

        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], '1')

   