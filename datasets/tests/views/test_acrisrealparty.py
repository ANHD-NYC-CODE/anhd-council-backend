from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class AcrisRealPartyViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        master = self.acrismaster_factory(documentid="1")
        self.acrisparty_factory(master=master)
        self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealparties/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        master = self.acrismaster_factory(documentid="1")
        party = self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealparties/{}/'.format(party.key))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["documentid"], '1')
