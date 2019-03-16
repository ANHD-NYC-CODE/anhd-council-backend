from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class AcrisRealMasterFilterTests(BaseTest, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_docamount_field(self):
        acrismaster1 = self.acrismaster_factory(documentid="a", doctype="DEED", docamount=10, docdate="2018-01-01")
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="DEED", docamount=1, docdate="2018-01-01")

        query = '/acrisrealmasters/?docamount__gte=10'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['documentid'], 'a')

    def test_doctype_field(self):
        acrismaster1 = self.acrismaster_factory(documentid="a", doctype="DEED", docdate="2018-01-01")
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="LEAS", docdate="2018-01-01")

        query = '/acrisrealmasters/?doctype=DEED'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['documentid'], 'a')

    def test_doctype_field(self):
        acrismaster1 = self.acrismaster_factory(documentid="a", doctype="DEED", docdate="2018-01-01")
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="LEAS", docdate="2018-01-01")
        acrismaster3 = self.acrismaster_factory(documentid="c", doctype="DEED, TS", docdate="2018-01-01")

        query = '/acrisrealmasters/?doctype__icontains=deed'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['documentid'], 'a')
        self.assertEqual(content[1]['documentid'], 'c')

    def test_docdate_field(self):
        acrismaster1 = self.acrismaster_factory(documentid="a", doctype="DEED", docdate="2018-01-01")
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="DEED", docdate="2010-01-01")
        acrismaster3 = self.acrismaster_factory(documentid="c", doctype="DEED", docdate="2018-01-01")

        query = '/acrisrealmasters/?docdate__gte=2018-01-01'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['documentid'], 'a')
        self.assertEqual(content[1]['documentid'], 'c')
