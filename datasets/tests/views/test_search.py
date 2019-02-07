from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class SearchTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_building_search_1(self):
        # Search:
        # 50 Main St
        building = self.building_factory()
        self.address_factory(building=building, number="50", letter="",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="52", letter="",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="12", letter="",
                             street="JONES DRIVE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=50 MAIN STREET', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['number'], "50")
        self.assertEqual(content[0]['street'], "MAIN STREET")

    def test_building_search_2(self):
        # Search:
        # 50 M
        building = self.building_factory()
        self.address_factory(building=building, number="50", letter="",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="52", letter="",
                             street="MAID STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="12", letter="",
                             street="MAINE AVENUE", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="50", letter="",
                             street="JONES AVENUE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=50 M', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_building_search_3(self):
        # Search:
        # 5 MA
        self.address_factory(number="50", letter="",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="52", letter="",
                             street="MAID DRIVE", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="12", letter="",
                             street="MOOSE AVENUE", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="50", letter="",
                             street="JONES AVENUE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=5 MA', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
