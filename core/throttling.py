from django.conf import settings
from rest_framework.throttling import AnonRateThrottle as DRFAnonRateThrottle
from rest_framework.throttling import UserRateThrottle as DRFUserRateThrottle


def is_internal_cache_request(request):
    """Bypass throttling for the nightly cache pre-warm task (whoisit header)."""
    cache_key = getattr(settings, 'CACHE_REQUEST_KEY', '')
    if not cache_key:
        return False
    return request.headers.get('whoisit') == cache_key


class InternalCacheExemptMixin:
    def allow_request(self, request, view):
        if is_internal_cache_request(request):
            return True
        return super().allow_request(request, view)


class AnonRateThrottle(InternalCacheExemptMixin, DRFAnonRateThrottle):
    scope = 'anon'


class UserRateThrottle(InternalCacheExemptMixin, DRFUserRateThrottle):
    scope = 'user'
