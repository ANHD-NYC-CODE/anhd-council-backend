from django.conf import settings
from django.http import JsonResponse

from core.throttling import is_internal_cache_request


class RejectPaginationQueryParamMiddleware:
    """Block ?page= on API routes — portal uses client-side table pagination only.

    DRF PageNumberPagination was opt-in via ?page= and is exploited by scrapers
    walking high page numbers. Django admin still uses ?page= for changelists.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not settings.TESTING
            and 'page' in request.GET
            and not request.path.startswith('/admin/')
            and not is_internal_cache_request(request)
        ):
            return JsonResponse(
                {'detail': 'Pagination is not supported on this API.'},
                status=403,
            )
        return self.get_response(request)
