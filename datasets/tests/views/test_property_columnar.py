import json

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings

from app.tests.base_test import BaseTest
from datasets.helpers.cache_helpers import (
    COLUMNAR_KEY_SUFFIX,
    scrub_columnar,
    to_columnar,
)

DASHBOARD = ('/councils/1/properties/?format=json&summary=true&summary-type=short-annotated'
             '&annotation__start=full&unitsres__gte=1')
COLUMNAR = DASHBOARD + '&shape=columnar'


def expand(payload):
    return [dict(zip(payload['columns'], row)) for row in payload['rows']]


class ColumnarTransformTests(SimpleTestCase):
    def test_round_trip_and_column_union(self):
        rows = [{'bbl': '1', 'a': 1}, {'bbl': '2', 'a': 2, 'b': 3}]
        value = to_columnar(rows)
        self.assertEqual(value['columns'], ['bbl', 'a', 'b'])
        self.assertEqual(value['rows'], [['1', 1, None], ['2', 2, 3]])

    def test_empty(self):
        self.assertEqual(to_columnar([]), {'columns': [], 'rows': []})

    def test_scrub_removes_protected_columns(self):
        value = to_columnar([{'bbl': '1', 'lispendens_recent__x': 1, 'foreclosures_lastyear__y': 2, 'hpd': 3}])
        self.assertEqual(scrub_columnar(value), {'columns': ['bbl', 'hpd'], 'rows': [['1', 3]]})


@override_settings(CACHE_REQUEST_KEY='internal-key')
class ColumnarViewTests(BaseTest, TestCase):
    def setUp(self):
        cache.clear()
        self.create_annotated_datasets()
        council = self.council_factory(id=1)
        for bbl in ('1', '2', '3'):
            prop = self.property_factory(bbl=bbl, council=council)
            self.hpdviolation_factory(property=prop)

    def tearDown(self):
        self.clean_tests()

    def _json(self, response):
        return json.loads(response.content)

    def _assert_columnar_matches_rows(self, **headers):
        rows = self._json(self.client.get(DASHBOARD, **headers))
        cache.clear()  # columnar computed fresh, then served from its own cache
        first = self.client.get(COLUMNAR, **headers)
        second = self.client.get(COLUMNAR, **headers)
        self.assertEqual(first.status_code, 200)
        for response in (first, second):
            payload = self._json(response)
            self.assertEqual(set(payload), {'columns', 'rows'})
            self.assertEqual(expand(payload), rows)
        return self._json(first)['columns']

    def test_columnar_matches_rows_anonymous(self):
        columns = self._assert_columnar_matches_rows()
        self.assertFalse(any('lispendens' in c or 'foreclosures' in c for c in columns))

    def test_columnar_matches_rows_trusted(self):
        token = self.get_access_token(trusted=True)
        columns = self._assert_columnar_matches_rows(HTTP_AUTHORIZATION=f'Bearer {token}')
        # Guards the anonymous scrub tests against passing vacuously.
        self.assertTrue(any('foreclosures' in c for c in columns), columns)

    def test_rows_request_also_caches_columnar_variant(self):
        # A pre-warm (whoisit, row shape) must leave columnar entries for both
        # trusted and anonymous keys, the anonymous one scrubbed.
        self.client.get(DASHBOARD, HTTP_WHOISIT='internal-key')
        keys = cache.keys('*' + COLUMNAR_KEY_SUFFIX)
        self.assertEqual(len(keys), 2)
        anon = self._json(self.client.get(COLUMNAR))
        self.assertEqual(len(anon['rows']), 3)
        self.assertFalse(any('lispendens' in c or 'foreclosures' in c for c in anon['columns']))

    def test_shape_param_is_not_part_of_cache_key(self):
        self.client.get(DASHBOARD)
        base_keys = set(cache.keys('/councils/1/properties/*'))
        self.client.get(COLUMNAR)
        self.assertFalse(any('shape' in key for key in cache.keys('*')))
        self.assertTrue(base_keys)

    def test_columnar_from_cached_rows_without_variant(self):
        rows = self._json(self.client.get(DASHBOARD))
        for key in cache.keys('*' + COLUMNAR_KEY_SUFFIX):
            cache.delete(key)
        self.assertEqual(expand(self._json(self.client.get(COLUMNAR))), rows)

    def test_non_dashboard_endpoint_ignores_shape(self):
        response = self.client.get('/councils/1/properties/?format=json&summary=true'
                                   '&summary-type=custom-search&housingtype=rs&shape=columnar')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(self._json(response), list)

    def test_capability_header(self):
        response = self.client.get(DASHBOARD)
        self.assertEqual(response['X-DAP-Shapes'], 'columnar')
