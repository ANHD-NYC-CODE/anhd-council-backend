from django.http import HttpRequest
from django.test import SimpleTestCase

from core.client_disconnect import is_custom_search_properties_request, query_was_cancelled
from django.db.utils import OperationalError


class CustomSearchDisconnectTests(SimpleTestCase):
    def test_matches_custom_search_properties_url(self):
        request = HttpRequest()
        request.path = '/councils/10/properties/'
        request.GET = {
            'summary': 'true',
            'summary-type': 'custom-search',
            'format': 'json',
            'q': '*condition_0=OR',
        }
        self.assertTrue(is_custom_search_properties_request(request))

    def test_ignores_other_property_summaries(self):
        request = HttpRequest()
        request.path = '/properties/'
        request.GET = {
            'summary': 'true',
            'summary-type': 'short-annotated',
            'format': 'json',
        }
        self.assertFalse(is_custom_search_properties_request(request))

    def test_query_was_cancelled_message(self):
        self.assertTrue(query_was_cancelled(OperationalError('canceling statement due to user request')))
