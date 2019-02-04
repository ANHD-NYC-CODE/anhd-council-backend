from django.test import TestCase
from django.urls import include, path
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class ForeclosureViewTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        response = self.client.get('/foreclosures/', format="json")

        self.assertEqual(response.status_code, 401)

    def test_retrieve(self):
        response = self.client.get('/foreclosures/1/')

        self.assertEqual(response.status_code, 401)
