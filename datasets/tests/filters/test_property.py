from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyFilterTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_yearbuilt_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council, yearbuilt=2000)
        property2 = self.property_factory(bbl=2, council=council, yearbuilt=1900)

        query = '/properties/?yearbuilt__gte=1950'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_hpdviolations_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)

        for i in range(10):
            self.hpdviolation_factory(property=property1)

        for i in range(5):
            self.hpdviolation_factory(property=property2)

        query = '/properties/?hpdviolations__gte=10'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_hpdviolationsdates_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")

        query = '/properties/?hpdviolations__start=2018-01-01&hpdviolations__end=2019-01-01&hpdviolations__gte=5'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')
