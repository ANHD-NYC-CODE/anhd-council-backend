from copy import deepcopy

from django.conf import settings
from django.test import override_settings

from app.tests.base_test import BaseTest


def _throttle_settings(anon='3/minute', user='5/minute'):
    rest_framework = deepcopy(settings.REST_FRAMEWORK)
    rest_framework['DEFAULT_THROTTLE_CLASSES'] = [
        'core.throttling.AnonRateThrottle',
        'core.throttling.UserRateThrottle',
    ]
    rest_framework['DEFAULT_THROTTLE_RATES'] = {
        'anon': anon,
        'user': user,
    }
    return rest_framework


@override_settings(
    REST_FRAMEWORK=_throttle_settings(),
    CACHE_REQUEST_KEY='test-cache-key',
)
class ThrottlingTests(BaseTest):

    def tearDown(self):
        self.clean_tests()

    def test_anonymous_requests_are_throttled(self):
        self.dataset_factory(name='Property')

        for _ in range(3):
            response = self.client.get('/datasets/?format=json')
            self.assertEqual(response.status_code, 200)

        response = self.client.get('/datasets/?format=json')
        self.assertEqual(response.status_code, 429)

    def test_authenticated_requests_have_higher_limit(self):
        self.dataset_factory(name='Property')
        token = self.get_access_token()

        for _ in range(5):
            response = self.client.get(
                '/datasets/?format=json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/datasets/?format=json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )
        self.assertEqual(response.status_code, 429)

    def test_internal_cache_header_bypasses_throttling(self):
        self.dataset_factory(name='Property')

        for _ in range(5):
            response = self.client.get(
                '/datasets/?format=json',
                HTTP_WHOISIT='test-cache-key',
            )
            self.assertEqual(response.status_code, 200)

    def test_wrong_internal_cache_header_is_throttled(self):
        self.dataset_factory(name='Property')

        for _ in range(3):
            response = self.client.get(
                '/datasets/?format=json',
                HTTP_WHOISIT='wrong-key',
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/datasets/?format=json',
            HTTP_WHOISIT='wrong-key',
        )
        self.assertEqual(response.status_code, 429)
