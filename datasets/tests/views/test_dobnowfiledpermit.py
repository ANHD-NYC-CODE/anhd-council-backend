from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class DOBNowFiledPermitTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.dobnowfiledpermit_factory()
        self.dobnowfiledpermit_factory()

        response = self.client.get('/dobnowfiledpermits/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        dobnowfiledpermit = self.dobnowfiledpermit_factory()

        response = self.client.get('/dobnowfiledpermits/{}/'.format(dobnowfiledpermit.jobfilingnumber))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["jobfilingnumber"], str(dobnowfiledpermit.jobfilingnumber))
