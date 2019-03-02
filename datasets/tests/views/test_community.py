from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class CommunitylViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.community_factory()
        self.community_factory()

        response = self.client.get('/communities/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.community_factory(id=1)

        response = self.client.get('/communities/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], 1)

    def test_community_properties(self):
        community = self.community_factory(id=1)
        self.property_factory(cd=community, bbl="1")
        self.property_factory(cd=community, bbl="2")

        response = self.client.get('/communities/1/properties/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_community_housing(self):
        community = self.community_factory(id=1)
        property1 = self.property_factory(cd=community, unitsres=10, yearbuilt=2000)
        property2 = self.property_factory(cd=community, unitsres=10, unitsrentstabilized=6, yearbuilt=1960)
        property3 = self.property_factory(cd=community, unitsres=10)
        property4 = self.property_factory(cd=community, unitsres=2)
        property5 = self.property_factory(cd=community, unitsres=10)
        self.taxbill_factory(property=property2, uc2016=10, uc2017=6)
        self.coredata_factory(property=property3, programname="j-51")
        self.publichousingrecord_factory(property=property5)

        response = self.client.get('/communities/1/housing/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["housing_types"]["residential_properties"]["count"], 5)
        self.assertEqual(content["housing_types"]["rent_stabilized"]["count"], 1)
        self.assertEqual(content["housing_types"]["rent_regulated"]["count"], 1)
        self.assertEqual(content["housing_types"]["small_homes"]["count"], 1)
        self.assertEqual(content["housing_types"]["market_rate"]["count"], 2)
        self.assertEqual(content["housing_types"]["public_housing"]["count"], 1)
        self.assertEqual(content["housing_types"]["rent_stabilized"]["units"], 6)
        self.assertEqual(content["housing_types"]["rent_regulated"]["units"], 10)
        self.assertEqual(content["housing_types"]["small_homes"]["units"], 2)
        self.assertEqual(content["housing_types"]["market_rate"]["units"], 12)
        self.assertEqual(content["housing_types"]["public_housing"]["units"], 10)
