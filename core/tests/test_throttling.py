from unittest import mock

from django.core.cache import cache
from django.test import override_settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from app.tests.base_test import BaseTest
from core.throttling import AnonRateThrottle, UserRateThrottle


# DRF binds throttle_classes / THROTTLE_RATES as class attributes at import time,
# so override_settings(REST_FRAMEWORK=...) never reaches them; patch the attributes instead.
@override_settings(CACHE_REQUEST_KEY='test-cache-key')
class ThrottlingTests(BaseTest):

    def setUp(self):
        cache.clear()  # throttle history lives in the default cache
        for target, attr, value in (
            (APIView, 'throttle_classes', [AnonRateThrottle, UserRateThrottle]),
            (SimpleRateThrottle, 'THROTTLE_RATES', {'anon': '3/minute', 'user': '5/minute'}),
        ):
            patcher = mock.patch.object(target, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)

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
