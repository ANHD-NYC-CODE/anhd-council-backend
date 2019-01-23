from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class DOBPermitIssuedLegacyTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.permitissuedlegacy_factory()
        self.permitissuedlegacy_factory()

        response = self.client.get('/doblegacyissuedpermits/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        doblegacyissuedpermits = self.permitissuedlegacy_factory()

        response = self.client.get('/doblegacyissuedpermits/{}/'.format(doblegacyissuedpermits.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], doblegacyissuedpermits.id)
