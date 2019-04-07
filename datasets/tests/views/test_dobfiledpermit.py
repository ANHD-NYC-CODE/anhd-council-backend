from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class DOBPermitFiledTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.dobfiledpermit_factory()
        self.dobfiledpermit_factory()

        response = self.client.get('/dobfiledpermits/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        dobfiledpermits = self.dobfiledpermit_factory()

        response = self.client.get('/dobfiledpermits/{}/'.format(dobfiledpermits.key))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["key"], dobfiledpermits.key)
