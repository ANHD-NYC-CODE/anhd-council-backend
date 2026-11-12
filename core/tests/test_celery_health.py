from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from app.tests.base_test import BaseTest
from core.celery_health import evaluate_celery_heartbeat, record_celery_heartbeat


class CeleryHealthLogicTests(TestCase):
    def tearDown(self):
        cache.clear()

    @override_settings(CELERY_HEARTBEAT_MAX_AGE_SECONDS=900)
    def test_evaluate_ok_when_fresh(self):
        record_celery_heartbeat()
        status = evaluate_celery_heartbeat()
        self.assertTrue(status['ok'])
        self.assertEqual(status['reason'], 'ok')

    @override_settings(CELERY_HEARTBEAT_MAX_AGE_SECONDS=60)
    def test_evaluate_stale_when_old(self):
        key = 'celery_heartbeat'
        old = timezone.now() - timedelta(minutes=5)
        cache.set(key, old.isoformat(), timeout=3600)
        status = evaluate_celery_heartbeat()
        self.assertFalse(status['ok'])
        self.assertEqual(status['reason'], 'stale')

    @override_settings(CELERY_HEARTBEAT_MAX_AGE_SECONDS=60)
    def test_evaluate_missing_heartbeat(self):
        status = evaluate_celery_heartbeat()
        self.assertFalse(status['ok'])
        self.assertEqual(status['reason'], 'no_heartbeat')


class CeleryHealthViewTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @override_settings(CELERY_HEARTBEAT_MAX_AGE_SECONDS=900)
    def test_health_endpoint_200_when_fresh(self):
        record_celery_heartbeat()
        response = self.client.get('/health/celery/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])

    @override_settings(CELERY_HEARTBEAT_MAX_AGE_SECONDS=900)
    def test_health_endpoint_503_when_missing(self):
        response = self.client.get('/health/celery/')
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()['ok'])
