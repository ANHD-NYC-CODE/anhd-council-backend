from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class ZipCodeViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.zipcode_factory(id=1)
        self.zipcode_factory(id=2)

        response = self.client.get('/zipcodes/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.zipcode_factory(id=1)

        response = self.client.get('/zipcodes/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], '1')

    def test_zipcode_properties(self):
        zipcode = self.zipcode_factory(id=1)
        self.property_factory(zipcode=zipcode, bbl="1")
        self.property_factory(zipcode=zipcode, bbl="2")

        response = self.client.get('/zipcodes/1/properties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
