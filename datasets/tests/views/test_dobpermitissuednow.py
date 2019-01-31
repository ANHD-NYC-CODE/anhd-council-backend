from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class DOBPermitIssuedNowTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.permitissuednow_factory()
        self.permitissuednow_factory()

        response = self.client.get('/dobnowissuedpermits/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        dobnowissuedpermits = self.permitissuednow_factory()

        response = self.client.get('/dobnowissuedpermits/{}/'.format(dobnowissuedpermits.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], dobnowissuedpermits.id)