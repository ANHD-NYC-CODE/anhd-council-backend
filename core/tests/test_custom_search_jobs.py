from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings

from app.tests.base_test import BaseTest
from core import custom_search_concurrency as conc
from core.custom_search_jobs import get_job_state, run_custom_search_job, set_job_state

JOBS_URL = '/properties/custom-search/jobs/'
CS_PARAMS = {'summary': 'true', 'summary-type': 'custom-search'}


def _reset_slots():
    cache.delete(conc.SLOT_KEY)


@override_settings(CUSTOM_SEARCH_MAX_CONCURRENT=2)
class ConcurrencySlotTests(TestCase):
    def setUp(self):
        _reset_slots()

    def tearDown(self):
        _reset_slots()

    def test_slots_limit_and_release(self):
        self.assertTrue(conc.try_acquire_slot())
        self.assertTrue(conc.try_acquire_slot())
        self.assertFalse(conc.try_acquire_slot())
        conc.release_slot()
        self.assertTrue(conc.try_acquire_slot())

    def test_context_manager_releases(self):
        with conc.custom_search_concurrency_slot() as a, conc.custom_search_concurrency_slot() as b:
            self.assertTrue(a and b)
            with conc.custom_search_concurrency_slot() as c:
                self.assertFalse(c)
        with conc.custom_search_concurrency_slot() as d:
            self.assertTrue(d)

    def test_blocking_acquire_times_out(self):
        conc.try_acquire_slot()
        conc.try_acquire_slot()
        self.assertFalse(conc.acquire_slot_blocking(timeout=0, poll_interval=0))


@mock.patch('core.tasks.async_run_custom_search_job.delay')
class CustomSearchJobViewTests(BaseTest, TestCase):
    def setUp(self):
        _reset_slots()

    def tearDown(self):
        self.clean_tests()

    def _start(self, path='/properties/', token=None, **params):
        body = {'path': path, 'params': {**CS_PARAMS, **params}}
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'} if token else {}
        return self.client.post(JOBS_URL, body, format='json', **headers)

    def test_rejects_invalid_path(self, delay):
        response = self._start(path='/users/', borough='MN', housingtype='rs')
        self.assertEqual(response.status_code, 400)
        delay.assert_not_called()

    def test_rejects_non_custom_search(self, delay):
        body = {'path': '/properties/', 'params': {'summary': 'true', 'summary-type': 'short-annotated'}}
        response = self.client.post(JOBS_URL, body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_rejects_citywide(self, delay):
        response = self._start(housingtype='rs')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Citywide', response.data['detail'])
        delay.assert_not_called()

    def test_rejects_unfiltered_borough(self, delay):
        response = self._start(borough='BK', housingtype='all')
        self.assertEqual(response.status_code, 400)
        delay.assert_not_called()

    def test_protected_query_requires_trusted_user(self, delay):
        q = '*condition_0=AND filter_0=lispendens__count__gte=1'
        response = self._start(borough='BK', q=q)
        self.assertEqual(response.status_code, 401)
        delay.assert_not_called()

        token = self.get_access_token(trusted=True)
        response = self._start(borough='BK', q=q, token=token)
        self.assertEqual(response.status_code, 202)

    def test_district_job_created(self, delay):
        response = self._start(path='/councils/1/properties/', housingtype='all')
        self.assertEqual(response.status_code, 202)
        job_id = response.data['job_id']
        delay.assert_called_once_with(job_id)
        state = get_job_state(job_id)
        self.assertEqual(state['path'], '/councils/1/properties/')
        self.assertEqual(state['query_params']['format'], 'json')
        self.assertEqual(state['status'], 'queued')

    def test_poll_scrubs_protected_fields_for_anonymous(self, delay):
        job_id = self._start(borough='BK', housingtype='rs').data['job_id']
        set_job_state(job_id, status='complete', percent=100, result=[
            {'bbl': '1', 'hpdviolations_0': 2, 'lispendens_0': 1, 'foreclosures_0': 1},
        ])
        response = self.client.get(f'{JOBS_URL}{job_id}/')
        self.assertEqual(response.status_code, 200)
        row = response.data['results'][0]
        self.assertEqual(row['hpdviolations_0'], 2)
        self.assertNotIn('lispendens_0', row)
        self.assertNotIn('foreclosures_0', row)
        self.assertEqual(response.data['result_count'], 1)

    def test_poll_keeps_protected_fields_for_trusted(self, delay):
        token = self.get_access_token(trusted=True)
        job_id = self._start(borough='BK', housingtype='rs', token=token).data['job_id']
        set_job_state(job_id, status='complete', percent=100, result=[{'bbl': '1', 'lispendens_0': 1}])
        response = self.client.get(f'{JOBS_URL}{job_id}/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.data['results'][0]['lispendens_0'], 1)

    def test_poll_refetch_when_result_too_large(self, delay):
        job_id = self._start(path='/councils/3/properties/', housingtype='rs').data['job_id']
        set_job_state(job_id, status='complete', percent=100, result=None)
        response = self.client.get(f'{JOBS_URL}{job_id}/')
        self.assertTrue(response.data['refetch'])
        self.assertEqual(response.data['path'], '/councils/3/properties/')
        self.assertEqual(response.data['query_params']['housingtype'], 'rs')

    def test_poll_unknown_job(self, delay):
        response = self.client.get(f'{JOBS_URL}00000000-0000-0000-0000-000000000000/')
        self.assertEqual(response.status_code, 404)

    def test_cancel(self, delay):
        job_id = self._start(borough='BK', housingtype='rs').data['job_id']
        response = self.client.delete(f'{JOBS_URL}{job_id}/')
        self.assertEqual(response.data['status'], 'cancelled')
        self.assertEqual(get_job_state(job_id)['status'], 'cancelled')


@override_settings(CUSTOM_SEARCH_MAX_CONCURRENT=1, CUSTOM_SEARCH_JOB_SLOT_WAIT=0,
                   CUSTOM_SEARCH_JOB_ORIGIN='http://origin:8000', CACHE_REQUEST_KEY='k')
class RunCustomSearchJobTests(TestCase):
    def setUp(self):
        _reset_slots()

    def tearDown(self):
        _reset_slots()
        cache.delete_pattern('custom_search:job:*')

    def _job(self, job_id='job-1', path='/councils/1/properties/'):
        set_job_state(job_id, status='queued', path=path,
                      query_params={**CS_PARAMS, 'housingtype': 'rs', 'format': 'json'})
        return job_id

    @mock.patch('core.custom_search_jobs.requests.get')
    def test_success_inline_and_releases_slot(self, get):
        get.return_value = mock.Mock(status_code=200, content=b'[{"bbl": "1"}]',
                                     json=lambda: [{'bbl': '1'}])
        job_id = self._job()
        run_custom_search_job(job_id)

        url = get.call_args[0][0]
        self.assertEqual(url, 'http://origin:8000/councils/1/properties/')
        self.assertEqual(get.call_args[1]['headers'], {'whoisit': 'k'})
        state = get_job_state(job_id)
        self.assertEqual(state['status'], 'complete')
        self.assertEqual(state['result'], [{'bbl': '1'}])
        self.assertTrue(conc.try_acquire_slot())  # slot was released

    @override_settings(CUSTOM_SEARCH_JOB_MAX_INLINE_BYTES=5)
    @mock.patch('core.custom_search_jobs.requests.get')
    def test_large_result_sets_refetch(self, get):
        get.return_value = mock.Mock(status_code=200, content=b'[{"bbl": "1"}]')
        job_id = self._job()
        run_custom_search_job(job_id)
        state = get_job_state(job_id)
        self.assertEqual(state['status'], 'complete')
        self.assertIsNone(state['result'])

    @mock.patch('core.custom_search_jobs.requests.get')
    def test_origin_error_fails_job(self, get):
        get.return_value = mock.Mock(status_code=400, json=lambda: {'detail': 'nope'})
        job_id = self._job()
        run_custom_search_job(job_id)
        state = get_job_state(job_id)
        self.assertEqual((state['status'], state['http_status'], state['error']), ('failed', 400, 'nope'))
        self.assertTrue(conc.try_acquire_slot())

    @mock.patch('core.custom_search_jobs.requests.get', side_effect=RuntimeError('boom'))
    def test_exception_fails_job_and_releases_slot(self, get):
        job_id = self._job()
        run_custom_search_job(job_id)
        self.assertEqual(get_job_state(job_id)['status'], 'failed')
        self.assertTrue(conc.try_acquire_slot())

    @mock.patch('core.custom_search_jobs.requests.get')
    def test_busy_fails_with_503(self, get):
        conc.try_acquire_slot()
        job_id = self._job()
        run_custom_search_job(job_id)
        state = get_job_state(job_id)
        self.assertEqual((state['status'], state['http_status']), ('failed', 503))
        get.assert_not_called()

    @mock.patch('core.custom_search_jobs.requests.get')
    def test_cancelled_job_skips_query(self, get):
        job_id = self._job()
        with mock.patch('core.custom_search_jobs.acquire_slot_blocking',
                        side_effect=lambda *a, **k: set_job_state(job_id, status='cancelled') and True):
            run_custom_search_job(job_id)
        get.assert_not_called()
        self.assertTrue(conc.try_acquire_slot())

    @mock.patch('core.custom_search_jobs.requests.get')
    def test_job_cancelled_before_pickup_stays_cancelled(self, get):
        job_id = self._job()
        set_job_state(job_id, status='cancelled')
        run_custom_search_job(job_id)
        get.assert_not_called()
        self.assertEqual(get_job_state(job_id)['status'], 'cancelled')


@override_settings(CACHE_REQUEST_KEY='internal-key')
class PropertyListPolicyViewTests(BaseTest, TestCase):
    CITYWIDE = '/properties/?format=json&housingtype=rs&summary=true&summary-type=custom-search'
    BOROUGH_ALL = '/properties/?format=json&borough=1&housingtype=all&summary=true&summary-type=custom-search'

    def setUp(self):
        _reset_slots()

    def tearDown(self):
        _reset_slots()
        self.clean_tests()

    def test_citywide_and_unfiltered_borough_rejected(self):
        self.assertEqual(self.client.get(self.CITYWIDE).status_code, 400)
        self.assertEqual(self.client.get(self.BOROUGH_ALL).status_code, 400)

    def test_internal_requests_exempt(self):
        # Saved-search notifications run citywide queries in Celery with whoisit.
        self.create_annotated_datasets()
        self.property_factory(bbl='1')
        self.assertEqual(self.client.get(self.CITYWIDE, HTTP_WHOISIT='internal-key').status_code, 200)
        self.assertEqual(self.client.get(self.BOROUGH_ALL, HTTP_WHOISIT='internal-key').status_code, 200)

    @override_settings(CUSTOM_SEARCH_MAX_CONCURRENT=1)
    def test_busy_returns_503_for_district_search(self):
        self.council_factory(id=1)
        conc.try_acquire_slot()
        response = self.client.get(
            '/councils/1/properties/?format=json&housingtype=rs&summary=true&summary-type=custom-search')
        self.assertEqual(response.status_code, 503)
        self.assertIn('Too many', response.data['detail'])


class HeartbeatPercentTests(TestCase):
    def test_monotonic_and_bounded(self):
        from core.custom_search_jobs import heartbeat_percent
        values = [heartbeat_percent(t) for t in (0, 10, 30, 60, 120, 300, 3000)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[0], 20)
        self.assertLessEqual(values[-1], 95)
        self.assertLess(heartbeat_percent(60), 90)  # still moving after a minute


class ResetCachePreservesJobsTests(TestCase):
    def tearDown(self):
        cache.delete_pattern('custom_search:*')

    @mock.patch('app.tasks.create_async_cache_workers')
    def test_reset_cache_keeps_jobs_and_slots_but_clears_responses(self, rebuild):
        from app.tasks import reset_cache
        set_job_state('job-keep', status='running', percent=40)
        conc.try_acquire_slot()
        cache.set('/councils/1/properties/?format=json', b'cached-response', timeout=600)

        reset_cache.run('token')

        self.assertEqual(get_job_state('job-keep')['percent'], 40)
        self.assertEqual(cache.get(conc.SLOT_KEY), 1)
        self.assertIsNone(cache.get('/councils/1/properties/?format=json'))
        self.assertGreater(cache.ttl('custom_search:job:job-keep'), 0)
        rebuild.assert_called_once_with('token')
