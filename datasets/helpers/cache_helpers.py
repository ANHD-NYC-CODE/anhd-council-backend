from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response

from copy import deepcopy
import urllib
from functools import wraps
import base64
import logging

logger = logging.getLogger('app')


def scrub_lispendens(cached_value, request, override=False):
    if override or not is_authenticated(request):
        if type(cached_value) is dict:
            if 'lispendens' in cached_value:
                del cached_value['lispendens']
            pass
        else:  # TEMP: only lists have the sensitive data for now.

            # filter out lispendens in annotated fields for unauthorized users
            if len(cached_value):
                lispendens_field = [key for key in cached_value[0].keys() if 'lispendens' in key]
                if len(lispendens_field):
                    for value in cached_value:
                        del value[lispendens_field[0]]
    return cached_value


def scrub_pagination(cached_value):
    if 'results' in cached_value:
        cached_value = cached_value['results']
    return cached_value


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
                cached_value = scrub_pagination(cached_value)
                cached_value = scrub_lispendens(cached_value, request)
                return original_args[0].finalize_response(request, Response(cached_value))
            else:
                response = function(*original_args, **original_kwargs)
                if (response.status_code == 200):
                    logger.debug('Caching: {}'.format(cache_key))
                    cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
                    if '__authenticated' in cache_key:  # also cache the scrubbed response for unauthenticated requests

                        cache_key = cache_key.replace('__authenticated', '')
                        logger.debug('Caching scrubbed varient: {}'.format(cache_key))
                        value_to_cache = scrub_pagination(response.data)
                        cache.set(cache_key, value_to_cache, timeout=settings.CACHE_TTL)
                logger.debug('Serving response: {}'.format(cache_key))
                return response
        return cached_view
    return cache_decorator

#
# def cache_property_list():
#     def cache_decorator(function):
#         @wraps(function)
#         def cached_view(*original_args, **original_kwargs):
#             request = original_args[1]
#             params = deepcopy(request.query_params)
#             params.pop('format', None)
#             params.pop('filename', None)
#
#             cache_key = '__'.join([*filter(None, request.path.split('/'))])
#             cache_key = cache_key + '__authenticated' if request.user.is_authenticated else cache_key
#
#             import pdb
#             pdb.set_trace()
#
#             cache_key = cache_key + '?' + urllib.parse.urlencode(params)
#
#             # TODO - figure out a way to inject cached data into renderer / response for browsable API pagination
#             # or skip caching on the django RF browsable api templates since they don't work ideally - loses pagination and filters
#             # if request.accepted_renderer.format == 'api':
#             #     return function(*original_args, **original_kwargs)
#             if cache_key in cache:
#                 # cached response will not display pagination buttons in browsable API view
#                 # but otherwise preserves the pagination data
#                 logger.debug('Serving cache: {}'.format(cache_key))
#                 cached_value = cache.get(cache_key)
#
#                 # don't serve paginated values with cache
#                 if 'results' in cached_value:
#                     cached_value = cached_value['results']
#
#                 if not request.user.is_authenticated:
#                     if type(cached_value) is dict:
#                         pass
#                     else:  # TEMP: only lists have the sensitive data for now.
#
#                         # filter out lispendens in annotated fields for unauthorized users
#                         if len(cached_value):
#                             lispendens_field = [key for key in cached_value[0].keys() if 'lispendens' in key]
#                             if len(lispendens_field):
#                                 for value in cached_value:
#                                     del value[lispendens_field[0]]
#
#                 return original_args[0].finalize_response(request, Response(cached_value))
#             else:
#                 response = function(*original_args, **original_kwargs)
#
#                 # cache only if response is 200
#                 if (response.status_code == 200):
#                     logger.debug('Caching: {}'.format(cache_key))
#
#                     cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
#                 return response
#
#         return cached_view
#     return cache_decorator
