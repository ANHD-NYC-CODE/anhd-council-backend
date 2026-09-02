from django.test import RequestFactory, SimpleTestCase, override_settings

from core.middleware import RejectPaginationQueryParamMiddleware


@override_settings(TESTING=False, CACHE_REQUEST_KEY='cache-warm-secret')
class RejectPaginationQueryParamMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RejectPaginationQueryParamMiddleware(lambda request: 'ok')

    def test_blocks_page_query_param(self):
        request = self.factory.get('/dobcomplaints/', {'format': 'json', 'page': '99'})
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Pagination is not supported', response.content.decode())

    def test_allows_requests_without_page(self):
        request = self.factory.get('/dobcomplaints/', {'format': 'json'})
        response = self.middleware(request)
        self.assertEqual(response, 'ok')

    def test_allows_admin_changelist_pagination(self):
        request = self.factory.get('/admin/datasets/dataset/', {'page': '2'})
        response = self.middleware(request)
        self.assertEqual(response, 'ok')

    def test_allows_internal_cache_warm_requests(self):
        request = self.factory.get(
            '/properties/',
            {'format': 'json', 'page': '1'},
            HTTP_WHOISIT='cache-warm-secret',
        )
        response = self.middleware(request)
        self.assertEqual(response, 'ok')
