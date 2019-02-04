from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class HPDBuildingViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdbuilding_factory(buildingid="1")
        self.hpdbuilding_factory(buildingid="2")

        response = self.client.get('/hpdbuildings/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        building = self.building_factory(bin="1")
        self.hpdbuilding_factory(buildingid="1", building=building)

        response = self.client.get('/hpdbuildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["buildingid"], 1)

    def test_hpdbuilding_violations(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdviolation_factory(hpdbuilding=hpdbuilding)
        self.hpdviolation_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_hpdbuilding_complaints(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdcomplaints/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_hpdbuilding_registrations(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdregistration_factory(hpdbuilding=hpdbuilding)
        self.hpdregistration_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdregistrations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
