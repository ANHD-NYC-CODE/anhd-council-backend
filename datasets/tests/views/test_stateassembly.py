from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class StateAssemblyViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.state_assembly_factory()
        self.state_assembly_factory()

        response = self.client.get('/stateassemblies/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.state_assembly_factory(id=1)

        response = self.client.get('/stateassemblies/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], 1)

    def test_stateassembly_properties(self):
        stateassembly = self.state_assembly_factory(id=1)
        self.property_factory(stateassembly=stateassembly, bbl="1")
        self.property_factory(stateassembly=stateassembly, bbl="2")

        response = self.client.get('/stateassemblies/1/properties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
