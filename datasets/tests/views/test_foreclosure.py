from django.test import TestCase
from django.urls import include, path
from app.tests.base_test import BaseTest
from datasets import models as ds
from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class LisPendenViewTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_unauthorized_list(self):
        response = self.client.get('/foreclosures/', format="json")

        self.assertEqual(response.status_code, 401)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/foreclosures/1/')

        self.assertEqual(response.status_code, 401)

    def test_list(self):
        self.lispenden_factory(type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'])
        self.lispenden_factory(type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'])

        token = self.get_access_token()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/foreclosures/', format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.lispenden_factory(key="1", type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'])
        token = self.get_access_token()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/foreclosures/1/')

        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["key"], "1")
