from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class BuildingViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.building_factory(bin="1")
        self.building_factory(bin="2")

        response = self.client.get('/buildings/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.building_factory(bin="1")

        response = self.client.get('/buildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["bin"], "1")

    def test_building_hpdviolations(self):
        building = self.building_factory(bin="1")
        self.hpdviolation_factory(building=building)
        self.hpdviolation_factory(building=building)

        response = self.client.get('/buildings/1/hpdviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_hpdcomplaints(self):
        building = self.building_factory(bin="1")
        hpdbuilding = self.hpdbuilding_factory(building=building)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/buildings/1/hpdcomplaints/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobviolations(self):
        building = self.building_factory(bin="1")
        self.dobviolation_factory(building=building)
        self.dobviolation_factory(building=building)

        response = self.client.get('/buildings/1/dobviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobcomplaints(self):
        building = self.building_factory(bin="1")
        self.dobcomplaint_factory(building=building)
        self.dobcomplaint_factory(building=building)

        response = self.client.get('/buildings/1/dobcomplaints/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_ecbviolations(self):
        building = self.building_factory(bin="1")
        self.ecbviolation_factory(building=building)
        self.ecbviolation_factory(building=building)

        response = self.client.get('/buildings/1/ecbviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_litigations(self):
        building = self.building_factory(bin="1")
        self.housinglitigation_factory(building=building)
        self.housinglitigation_factory(building=building)

        response = self.client.get('/buildings/1/housinglitigations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_registrations(self):
        building = self.building_factory(bin="1")
        self.hpdregistration_factory(building=building)
        self.hpdregistration_factory(building=building)

        response = self.client.get('/buildings/1/hpdregistrations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_doblegacyissuedpermits(self):
        building = self.building_factory(bin="1")
        self.permitissuedlegacy_factory(building=building)
        self.permitissuedlegacy_factory(building=building)

        response = self.client.get('/buildings/1/doblegacyissuedpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobnowissuedpermits(self):
        building = self.building_factory(bin="1")
        self.permitissuednow_factory(building=building)
        self.permitissuednow_factory(building=building)

        response = self.client.get('/buildings/1/dobnowissuedpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_doblegacyfiledpermits(self):
        building = self.building_factory(bin="1")
        self.permitfiledlegacy_factory(building=building)
        self.permitfiledlegacy_factory(building=building)

        response = self.client.get('/buildings/1/doblegacyfiledpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
