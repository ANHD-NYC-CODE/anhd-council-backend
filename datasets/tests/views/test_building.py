from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class BuildingViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.building_factory(bin="1")
        self.building_factory(bin="2")

        response = self.client.get('/buildings/', format="json")
        content = response.data

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
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_hpdcomplaints(self):
        building = self.building_factory(bin="1")
        self.hpdcomplaint_factory(building=building)
        self.hpdcomplaint_factory(building=building)

        response = self.client.get('/buildings/1/hpdcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobviolations(self):
        building = self.building_factory(bin="1")
        self.dobviolation_factory(building=building)
        self.dobviolation_factory(building=building)

        response = self.client.get('/buildings/1/dobviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobcomplaints(self):
        building = self.building_factory(bin="1")
        self.dobcomplaint_factory(building=building)
        self.dobcomplaint_factory(building=building)

        response = self.client.get('/buildings/1/dobcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_ecbviolations(self):
        building = self.building_factory(bin="1")
        self.ecbviolation_factory(building=building)
        self.ecbviolation_factory(building=building)

        response = self.client.get('/buildings/1/ecbviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_litigations(self):
        building = self.building_factory(bin="1")
        self.housinglitigation_factory(building=building)
        self.housinglitigation_factory(building=building)

        response = self.client.get('/buildings/1/housinglitigations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_registrations(self):
        building = self.building_factory(bin="1")
        self.hpdregistration_factory(building=building)
        self.hpdregistration_factory(building=building)

        response = self.client.get('/buildings/1/hpdregistrations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobpermitissuedlegacy(self):
        building = self.building_factory(bin="1")
        self.permitissuedlegacy_factory(building=building)
        self.permitissuedlegacy_factory(building=building)

        response = self.client.get('/buildings/1/dobpermitissuedlegacy/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobpermitissuednow(self):
        building = self.building_factory(bin="1")
        self.permitissuednow_factory(building=building)
        self.permitissuednow_factory(building=building)

        response = self.client.get('/buildings/1/dobpermitissuednow/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobissuedpermits(self):
        building = self.building_factory(bin="1")
        self.dobissuedpermit_factory(building=building)
        self.dobissuedpermit_factory(building=building)

        response = self.client.get('/buildings/1/dobissuedpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobfiledpermits(self):
        building = self.building_factory(bin="1")
        self.dobfiledpermit_factory(building=building)
        self.dobfiledpermit_factory(building=building)

        response = self.client.get('/buildings/1/dobfiledpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_doblegacyfiledpermit(self):
        building = self.building_factory(bin="1")
        self.doblegacyfiledpermit_factory(building=building)
        self.doblegacyfiledpermit_factory(building=building)

        response = self.client.get('/buildings/1/doblegacyfiledpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
