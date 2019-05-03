from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
import gzip
import json
from rest_framework.utils.serializer_helpers import ReturnDict
from copy import deepcopy
import urllib
from functools import wraps
import base64
import logging

logger = logging.getLogger('app')


def scrub_pagination(cached_value):
    if 'results' in cached_value:
        cached_value = cached_value['results']

    return cached_value


def scrub_lispendens(cached_value, request):
    if not is_authenticated(request):
        if type(cached_value) is dict or isinstance(cached_value, ReturnDict):
            if 'lispendens' in cached_value:
                del cached_value['lispendens']
            pass
        else:  # TEMP: only lists have the sensitive data for now.

            # filter out lispendens in annotated fields for unauthorized users
            if len(cached_value):

                lispendens_fields = [key for key in cached_value[0].keys() if 'lispendens' in key]
                if len(lispendens_fields):
                    for value in cached_value:
                        for field in lispendens_fields:
                            del value[field]
    return cached_value


def decompress_cache(cached_value):

    return json.loads(gzip.decompress(cached_value).decode('utf-8'))


def compress_cache(cached_value):
    # convert datetimes to be json serializable
    json_value = json.dumps(cached_value, default=lambda o: o.isoformat() if hasattr(o, 'isoformat') else o)
    return gzip.compress(json_value.encode('utf-8'))


def is_authenticated(request):
    return request.user.is_authenticated or 'whoisit' in request.headers and request.headers['whoisit'] == settings.CACHE_REQUEST_KEY


def construct_cache_key(request, params):
    params.pop('format', None)
    params.pop('filename', None)
    cache_key = request.path + '?' + urllib.parse.urlencode(params)
    # if is_authenticated(request):
    #     cache_key = cache_key + '__authenticated'
    return cache_key


def cache_request_path():
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):
            request = original_args[1]
            params = deepcopy(request.query_params)
            cache_key = construct_cache_key(request, params)

            if cache_key in cache:
                logger.debug('Serving cache: {}'.format(cache_key))
                cached_value = cache.get(cache_key)
                cached_value = decompress_cache(cached_value)
                cached_value = scrub_lispendens(cached_value, request)
                return original_args[0].finalize_response(request, Response(cached_value))
            else:
                response = function(*original_args, **original_kwargs)
                if (response.status_code == 200):
                    value_to_cache = response.data
                    value_to_cache = scrub_pagination(value_to_cache)
                    value_to_cache = compress_cache(value_to_cache)
                    logger.debug('Caching: {}'.format(cache_key))

                    cache.set(cache_key, value_to_cache, timeout=settings.CACHE_TTL)
                    # if '__authenticated' in cache_key:  # also cache the scrubbed response for unauthenticated requests
                    #     cache_key = cache_key.replace('__authenticated', '')
                    #     logger.debug('Caching scrubbed varient: {}'.format(cache_key))
                    #     cache.set(cache_key, value_to_cache, timeout=settings.CACHE_TTL)
                logger.debug('Serving response: {}'.format(cache_key))
                scrubbed_response = scrub_pagination(response.data)  # TODO: remove pagination altogether
                scrubbed_response = scrub_lispendens(scrubbed_response, request)
                return original_args[0].finalize_response(request, Response(scrubbed_response))
        return cached_view
    return cache_decorator
