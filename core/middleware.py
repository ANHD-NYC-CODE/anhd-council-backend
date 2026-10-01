from django.conf import settings
from django.db.utils import DatabaseError, OperationalError
from django.http import HttpResponse, JsonResponse

from core.client_disconnect import client_disconnect_guard, handle_cancelled_search_exception
from core.client_disconnect import is_custom_search_properties_request
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


class CancelCustomSearchOnDisconnectMiddleware:
    """Cancel in-flight Postgres work when the portal aborts a custom search GET."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.TESTING or not is_custom_search_properties_request(request):
            return self.get_response(request)

        with client_disconnect_guard(request):
            try:
                return self.get_response(request)
            except (OperationalError, DatabaseError) as exc:
                if handle_cancelled_search_exception(exc):
                    return HttpResponse(status=499)
                raise
