from django.core.cache import cache
from django.conf import settings

from datasets import models as ds
from functools import wraps
import logging

logger = logging.getLogger('app')


def cache_me(relative_key_path=True, get_queryset=False):
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):
            cache_key = original_args[1].build_absolute_uri()

            if cache_key in cache:
                logger.debug('Serving cache: {}'.format(cache_key))
                return Response(cache.get(cache_key))
            else:
                response = function(*original_args, **original_kwargs)

                logger.debug('Caching: {}'.format(cache_key))
                cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
                return response

        return cached_view
    return cache_decorator


def properties_by_housingtype(request, queryset=None):
    if not queryset:
        queryset = ds.Property.objects

    if 'housingtype' in request.query_params:
        housingtype = request.query_params['housingtype']
    else:
        housingtype = None

    switcher = {
        "rent-stabilized": queryset.rentstab(),
        "rent-regulated": queryset.rentreg(),
        "small-homes": queryset.smallhome(),
        "market-rate": queryset.marketrate()
    }

    return switcher.get(housingtype, queryset)
