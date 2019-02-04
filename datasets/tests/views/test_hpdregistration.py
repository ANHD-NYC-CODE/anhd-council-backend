from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class HPDRegistrationViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdregistration_factory(registrationid="1")
        self.hpdregistration_factory(registrationid="2")

        response = self.client.get('/hpdregistrations/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        hpdregistration = self.hpdregistration_factory(registrationid="1")

        response = self.client.get('/hpdregistrations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["registrationid"], 1)

    def test_hpdregistration_hpdcontacts(self):
        registration = self.hpdregistration_factory(registrationid="1")
        self.hpdcontact_factory(registration=registration)
        self.hpdcontact_factory(registration=registration)

        response = self.client.get('/hpdregistrations/1/hpdcontacts/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
