from django.conf import settings
from rest_framework.throttling import AnonRateThrottle as DRFAnonRateThrottle
from rest_framework.throttling import UserRateThrottle as DRFUserRateThrottle
from rest_framework.throttling import SimpleRateThrottle


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


class CustomSearchJobRateThrottle(InternalCacheExemptMixin, SimpleRateThrottle):
    """Per user (or IP) cap on starting custom-search jobs."""
    scope = 'custom_search_job'
    rate = '20/minute'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class AnonRateThrottle(InternalCacheExemptMixin, DRFAnonRateThrottle):
    scope = 'anon'


class UserRateThrottle(InternalCacheExemptMixin, DRFUserRateThrottle):
    scope = 'user'
