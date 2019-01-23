from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class AcrisRealMasterViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.acrismaster_factory(documentid="1")
        self.acrismaster_factory(documentid="2")

        response = self.client.get('/acrisrealmasters/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.acrismaster_factory(documentid="1")

        response = self.client.get('/acrisrealmasters/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["documentid"], '1')

    def test_acrismaster_acrisparties(self):
        master = self.acrismaster_factory(documentid="1")
        self.acrisparty_factory(master=master)
        self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealmasters/1/acrisrealparties/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
