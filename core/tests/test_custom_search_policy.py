from django.test import SimpleTestCase
from django.test import RequestFactory

from core.custom_search_policy import (
    is_any_custom_search_json_list,
    is_blocked_borough_unfiltered_custom_search,
    is_blocked_citywide_custom_search,
    is_custom_search_json_list,
    is_valid_custom_search_path,
    q_references_protected_dataset,
)


class CustomSearchPolicyTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_custom_search_json_list(self):
        request = self.factory.get(
            '/properties/',
            {
                'format': 'json',
                'summary': 'true',
                'summary-type': 'custom-search',
                'borough': 'BK',
            },
        )
        self.assertTrue(is_custom_search_json_list(request))

    def test_blocks_borough_all_no_filters(self):
        request = self.factory.get(
            '/properties/',
            {
                'format': 'json',
                'housingtype': 'all',
                'borough': 'BK',
                'summary': 'true',
                'summary-type': 'custom-search',
            },
        )
        self.assertTrue(is_blocked_borough_unfiltered_custom_search(request))

    def test_allows_borough_with_housing_type(self):
        request = self.factory.get(
            '/properties/',
            {
                'format': 'json',
                'housingtype': 'rs',
                'borough': 'BK',
                'summary': 'true',
                'summary-type': 'custom-search',
            },
        )
        self.assertFalse(is_blocked_borough_unfiltered_custom_search(request))

    def test_allows_borough_with_q_filters(self):
        request = self.factory.get(
            '/properties/',
            {
                'format': 'json',
                'housingtype': 'all',
                'borough': 'BK',
                'summary': 'true',
                'summary-type': 'custom-search',
                'q': '*condition_0=AND filter_0=hpdviolations__count__gte=1',
            },
        )
        self.assertFalse(is_blocked_borough_unfiltered_custom_search(request))


class CustomSearchGeographyPolicyTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _cs(self, path='/properties/', **extra):
        params = {'format': 'json', 'summary': 'true', 'summary-type': 'custom-search'}
        params.update(extra)
        return self.factory.get(path, params)

    def test_blocks_citywide(self):
        self.assertTrue(is_blocked_citywide_custom_search(self._cs(housingtype='rs')))

    def test_borough_is_not_citywide(self):
        self.assertFalse(is_blocked_citywide_custom_search(self._cs(borough='MN')))

    def test_district_query_param_is_not_citywide(self):
        self.assertFalse(is_blocked_citywide_custom_search(self._cs(council='1')))
        self.assertFalse(is_blocked_citywide_custom_search(self._cs(zipcode='10001')))

    def test_nested_district_path_not_blocked(self):
        request = self._cs('/councils/1/properties/', housingtype='all')
        self.assertFalse(is_blocked_citywide_custom_search(request))
        self.assertFalse(is_blocked_borough_unfiltered_custom_search(request))
        self.assertTrue(is_any_custom_search_json_list(request))

    def test_non_custom_search_summary_not_blocked(self):
        request = self.factory.get('/properties/', {
            'format': 'json', 'summary': 'true', 'summary-type': 'short-annotated',
            'annotation__start': 'full', 'unitsres__gte': '1',
        })
        self.assertFalse(is_blocked_citywide_custom_search(request))
        self.assertFalse(is_any_custom_search_json_list(request))

    def test_valid_custom_search_paths(self):
        for path in ('/properties/', '/councils/12/properties/', '/communities/101/properties/',
                     '/stateassemblies/5/properties/', '/statesenates/5/properties/',
                     '/zipcodes/10001/properties/'):
            self.assertTrue(is_valid_custom_search_path(path), path)
        for path in ('/users/', '/councils/x/properties/', '/properties/1/', 'http://evil/properties/',
                     '/councils/1/properties/../../users/', ''):
            self.assertFalse(is_valid_custom_search_path(path), path)

    def test_protected_q_detection(self):
        self.assertTrue(q_references_protected_dataset('*condition_0=AND filter_0=lispendens__count__gte=1'))
        self.assertFalse(q_references_protected_dataset('*condition_0=AND filter_0=hpdviolations__count__gte=1'))
        self.assertFalse(q_references_protected_dataset(None))
