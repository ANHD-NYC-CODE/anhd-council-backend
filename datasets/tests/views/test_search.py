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
        building = self.building_factory(lhnd="50", hhnd="52")
        building2 = self.building_factory(lhnd="100", hhnd="52")

        self.address_factory(building=building, number="50", buildingnumber="50-52",
                             street="MAIN STREET", buildingstreet="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building,  number="52",
                             street="MAIN STREET", buildingnumber="50-52",
                             buildingstreet="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building2,  number="100",
                             street="JONES DRIVE", buildingnumber="100",
                             buildingstreet="JONES DRIVE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=50 MAIN STREET', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['buildingnumber'], "50-52")
        self.assertEqual(content[0]['buildingstreet'], "MAIN STREET")

    def test_building_search_2(self):
        # Search:
        # 50 M
        building = self.building_factory()
        self.address_factory(building=building, number="50",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="52",
                             street="MAID STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="12",
                             street="MAINE AVENUE", borough="Brooklyn", zipcode='11111')
        self.address_factory(building=building, number="50",
                             street="JONES AVENUE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=50 M', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_building_search_3(self):
        # Search:
        # 5 MA
        self.address_factory(number="50",
                             street="MAIN STREET", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="52",
                             street="MAID DRIVE", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="12",
                             street="MOOSE AVENUE", borough="Brooklyn", zipcode='11111')
        self.address_factory(number="50",
                             street="JONES AVENUE", borough="Brooklyn", zipcode='11111')

        ds.AddressRecord.build_search()

        response = self.client.get('/search/buildings/?fts=5 MA', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
