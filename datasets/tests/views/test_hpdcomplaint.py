from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class HPDComplaintViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdcomplaint_factory(complaintid="1")
        self.hpdcomplaint_factory(complaintid="2")

        response = self.client.get('/hpdcomplaints/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.hpdcomplaint_factory(complaintid="1")

        response = self.client.get('/hpdcomplaints/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["complaintid"], 1)

    def test_hpdcomplaint_hpdproblems(self):
        complaint = self.hpdcomplaint_factory(complaintid="1")
        self.hpdproblem_factory(complaint=complaint)
        self.hpdproblem_factory(complaint=complaint)

        response = self.client.get('/hpdcomplaints/1/hpdproblems/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)