from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class StateSenateViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.state_senate_factory()
        self.state_senate_factory()

        response = self.client.get('/statesenates/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.state_senate_factory(id=1)

        response = self.client.get('/statesenates/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], 1)

    def test_statesenate_properties(self):
        statesenate = self.state_senate_factory(id=1)
        self.property_factory(statesenate=statesenate, bbl="1")
        self.property_factory(statesenate=statesenate, bbl="2")

        response = self.client.get('/statesenates/1/properties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
