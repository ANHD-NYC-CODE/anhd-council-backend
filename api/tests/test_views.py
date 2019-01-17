from django.test import TestCase, RequestFactory
from app.tests.base_test import BaseTest


from api.views import councils_index

import logging
logging.disable(logging.CRITICAL)


class CouncilsIndexTests(BaseTest, TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        self.clean_tests()

    def test_api_request(self):
        self.council_factory()
        request = self.factory.get('/councils')
        response = councils_index(request)
        self.assertEqual(response.status_code, 200)
