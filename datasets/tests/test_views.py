from django.test import TestCase, RequestFactory
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import json
import logging
logging.disable(logging.CRITICAL)


class CouncilViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_council_list(self):
        self.council_factory()

        response = self.client.get('/councils/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_council_retrieve(self):
        council = self.council_factory(coundist=1)

        response = self.client.get('/councils/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["coundist"], 1)

    def test_council_properties(self):
        council = self.council_factory(coundist=1)
        self.property_factory(council=council, bbl="1")
        self.property_factory(council=council, bbl="2")

        response = self.client.get('/councils/1/properties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_council_housingtype_summary(self):
        council = self.council_factory(coundist=1)
        self.property_factory(council=council)

        response = self.client.get('/councils/1/housingtype-summary/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["housing_types"]["market_rate_count"], 1)


class PropertyViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def test_property_list(self):
        council = self.council_factory(coundist=1)
        self.property_factory(council=council, bbl="1")
        self.property_factory(council=council, bbl="2")

        response = self.client.get('/properties/')
        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_retrieve(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council, bbl="1", yearbuilt="1910")
        # hpdbuilding = self.hpdbuilding_factory(property=property, building=building1)
        #
        # self.hpdcomplaint_factory(property=property, hpdbuilding=hpdbuilding, status="ACTIVE")
        # self.hpdviolation_factory(property=property, building=building1)

        response = self.client.get('/properties/1/')
        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['bbl'], '1')
        self.assertEqual(content['yearbuilt'], 1910)
        # self.assertEqual(content['hpdcomplaints']['total'], 1)
        # self.assertEqual(content['hpdcomplaints']['items'][0]["status"], "ACTIVE")
        # self.assertEqual(content['hpdviolations']['total'], 1)
        # self.assertEqual(content['hpdviolations']['items'][0]["currentstatus"], "ACTIVE")

    def test_property_buildings(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council, bbl="1")
        self.building_factory(bin="1", property=property)
        self.building_factory(bin="2", property=property)

        response = self.client.get('/properties/1/buildings/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdbuildings(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council, bbl="1")
        building1 = self.building_factory(bin="1", property=property)
        building2 = self.building_factory(bin="2", property=property)
        self.hpdbuilding_factory(buildingid="1", property=property, building=building1)
        self.hpdbuilding_factory(buildingid="2", property=property, building=building2)

        response = self.client.get('/properties/1/hpdbuildings/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_buildings_summary(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)
        building1 = self.building_factory(property=property, bin="10a", lhnd="100", hhnd="100")
        building2 = self.building_factory(property=property, bin="10b", lhnd="102", hhnd="102")

        response = self.client.get('/properties/1/buildings-summary/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["buildings"]["items"]), 2)
        self.assertEqual(content["buildings"]["items"][0]["house_number"], "102")


class BuildingViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_building_list(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)
        self.building_factory(bin="1", property=property)
        self.building_factory(bin="2", property=property)

        response = self.client.get('/buildings/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_retrieve(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)
        self.building_factory(bin="1", property=property)

        response = self.client.get('/buildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["bin"], "1")


class HPDBuildingViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_building_list(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)
        building1 = self.building_factory(bin="1", property=property)
        building2 = self.building_factory(bin="2", property=property)
        self.hpdbuilding_factory(buildingid="1", property=property, building=building1)
        self.hpdbuilding_factory(buildingid="2", property=property, building=building2)

        response = self.client.get('/hpdbuildings/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_retrieve(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)
        building = self.building_factory(bin="1", property=property)
        self.hpdbuilding_factory(buildingid="1", property=property, building=building)

        response = self.client.get('/hpdbuildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["buildingid"], 1)
