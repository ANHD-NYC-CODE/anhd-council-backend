from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class PropertyAnnotationViewTests(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_list_unauthenticated(self):
        # unauthenticated
        property = self.property_factory(bbl='1')
        property.propertyannotation.lispendens_last30 = 1
        property.propertyannotation.save()

        response = self.client.get('/propertyannotations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual('lispendens_last30' in content[0], False)
        self.assertEqual('lispendens_lastyear' in content[0], False)
        self.assertEqual('lispendens_last3years' in content[0], False)

    def test_list_authenticated(self):
        # authenticated
        property = self.property_factory(bbl='1')
        property.propertyannotation.lispendens_last30 = 1
        property.propertyannotation.save()

        token = self.get_access_token()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/propertyannotations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['lispendens_last30'], 1)
        self.assertEqual('lispendens_lastyear' in content[0], True)
        self.assertEqual('lispendens_last3years' in content[0], True)

    def test_retrieve(self):
        property = self.property_factory(bbl='1')
        property.propertyannotation.lispendens_last30 = 1
        property.propertyannotation.save()

        response = self.client.get('/propertyannotations/{}/'.format(property.propertyannotation.pk))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["bbl"], '1')
        self.assertEqual('lispendens_last30' in content, False)
        self.assertEqual('lispendens_lastyear' in content, False)
        self.assertEqual('lispendens_last3years' in content, False)
