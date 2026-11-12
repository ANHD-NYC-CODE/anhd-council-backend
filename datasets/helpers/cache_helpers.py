from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
import gzip
import json
from rest_framework.utils.serializer_helpers import ReturnDict
from copy import deepcopy
import urllib
from functools import wraps
import base64
from rest_framework import status
from users.permission import _has_group_permission

import logging

logger = logging.getLogger('app')

# Refuse to cache compressed response bodies bigger than this. Defense in depth
# against a single huge response monopolizing Redis memory (we found a 350MB
# entry at /dobpermitissuednow/?page=6435 from a CSV poisoning the JSON cache
# before we separated the format from the cache key — see construct_cache_key).
MAX_CACHE_VALUE_BYTES = 100 * 1024 * 1024  # 100 MB compressed

# 7-day TTL applied to borough-wide and citywide /properties/ aggregates.
# Those entries are heavy (5+ min cold for BK), but they change slowly at
# the borough aggregate level — PLUTO refreshes quarterly, RS annually,
# the daily-cadence datasets (HPD/DOB/eviction counts) only nudge a small
# fraction of properties in any given day. 7-day TTL bridges the gap
# between the weekly Sunday pre-warm runs; if a structural dataset
# refreshes (PLUTO etc.), the seed-success hook invalidates these keys
# explicitly so the next user request rebuilds with fresh data.
HEAVY_GEOGRAPHIC_CACHE_TTL = 7 * 24 * 60 * 60  # 7 days


def _is_heavy_geographic_url(request):
    """True for the borough-wide / citywide /properties/ summary URLs that
    the pre-warm targets. Used to apply HEAVY_GEOGRAPHIC_CACHE_TTL rather
    than the default CACHE_TTL."""
    if request.path != '/properties/':
        return False
    params = request.query_params
    # All the pre-warm URLs use summary=true + summary-type=short-annotated
    # + annotation__start=full. Any other URL hitting /properties/ is
    # filtered/paginated and stays on the default TTL.
    return (
        params.get('summary') == 'true'
        and params.get('summary-type') == 'short-annotated'
        and params.get('annotation__start') == 'full'
    )
# Raised stepwise on 2026-06-25:
#   5 MB → 50 MB (b commit) — covered MN/BX/SI boroughs.
#   50 MB → 100 MB (c commit) — adds BK (~50-80 MB) and QN (~55-90 MB).
# Cache budget at 100 MB cap is ~575-700 MB total (existing 450 MB
# dashboard pre-warms + ~125-220 MB for 5 boroughs), well under the
# 4 GB Redis maxmemory. Citywide (~150-200 MB compressed) still likely
# exceeds the cap and will fall back to per-request fetch — accepted
# because citywide is a power-user/bot URL, not a critical user flow.
# Per-request decompress of a 100 MB entry produces ~1 GB JSON
# transiently per worker; with 3 workers × 4 threads on prod, worst-
# case concurrent decompress = ~3 GB, well within the 31 GB host RAM.


def has_cachable_format(request):
    if settings.TESTING:
        return True

    params = request.query_params

    # Only cache JSON. CSV responses are bulk exports (often the full table),
    # rarely re-hit, and dwarf normal API payloads — caching them in Redis was
    # the source of the multi-hundred-MB poisoned cache entries we cleaned up.
    return 'format' in params.keys() and 'json' in params['format']


def scrub_pagination(cached_value):
    if 'results' in cached_value:
        cached_value = cached_value['results']

    return cached_value


def scrub_authenticated(cached_value, request):
    if not is_authenticated(request):
        if type(cached_value) is dict or isinstance(cached_value, ReturnDict):
            if 'lispendens' in cached_value:
                del cached_value['lispendens']
            if 'foreclosures' in cached_value:
                del cached_value['foreclosures']
            if 'foreclosure-auctions' in cached_value:
                del cached_value['foreclosure-auctions']
            if 'ocahousingcourts' in cached_value:
                del cached_value['ocahousingcourts']
            pass
        else:  # TEMP: only lists have the sensitive data for now.

            # filter out lispendens in annotated fields for unauthorized users
            if len(cached_value):
                lispendens_fields = [
                    key for key in cached_value[0].keys() if key and 'lispendens' in key]
                if len(lispendens_fields):
                    for value in cached_value:
                        for field in lispendens_fields:
                            del value[field]

                foreclosures_field = [
                    key for key in cached_value[0].keys() if key and 'foreclosures' in key]
                if len(foreclosures_field):
                    for value in cached_value:
                        for field in foreclosures_field:
                            del value[field]
    return cached_value


def decompress_cache(cached_value):

    return json.loads(gzip.decompress(cached_value).decode('utf-8'))


def compress_cache(cached_value):
    # convert datetimes to be json serializable
    json_value = json.dumps(
        cached_value, default=lambda o: o.isoformat() if hasattr(o, 'isoformat') else o)
    return gzip.compress(json_value.encode('utf-8'))


def is_authenticated(request):
    return (request.user.is_authenticated and _has_group_permission(request.user, ['trusted'])) or 'whoisit' in request.headers and request.headers['whoisit'] == settings.CACHE_REQUEST_KEY


def construct_cache_key(request, params):
    # NOTE: do NOT pop `format` here. Stripping it caused CSV responses
    # (unpaginated full tables — easily 100+ MB) to share cache slots with
    # paginated JSON responses (~100 KB), poisoning Redis with hundreds of MB
    # per key. CSV is no longer cached at all (see has_cachable_format), but
    # keep format in the key as defense in depth.
    params.pop('filename', None)
    cache_key = request.path + '?' + urllib.parse.urlencode(params)
    if is_authenticated(request):
        cache_key = cache_key + '__authenticated'
    return cache_key


# ---------------------------------------------------------------------------
# Columnar response shape (`shape=columnar`) for property summary lists.
#
# Row objects repeat ~48 long, date-stamped keys per property
# ("hpdviolations_last3years__11/12/2023-06/10/2026"), which is ~90% of the
# JSON. Columnar sends {"columns": [...], "rows": [[...], ...]} instead:
# citywide `annotation__start=full` drops from ~1.47 GB to ~154 MB raw.
#
# `shape` is never part of the cache key, so row and columnar clients share
# the same pre-warmed entry. The columnar variant is cached next to it
# (`<key>__columnar`), stored already scrubbed for the unauthenticated key,
# so hits are served as stored bytes without a JSON parse/render.
# ---------------------------------------------------------------------------
SHAPE_PARAM = 'shape'
COLUMNAR_SHAPE = 'columnar'
COLUMNAR_KEY_SUFFIX = '__columnar'
AUTHENTICATED_KEY_SUFFIX = '__authenticated'
# Same column terms scrub_authenticated removes from row lists.
PROTECTED_COLUMN_TERMS = ('lispendens', 'foreclosures')


def is_columnar_eligible(request):
    params = request.query_params
    return (
        request.path.endswith('properties/')
        and params.get('summary') == 'true'
        and params.get('summary-type', '').lower() == 'short-annotated'
    )


def to_columnar(rows):
    columns = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return {'columns': columns, 'rows': [[row.get(c) for c in columns] for row in rows]}


def scrub_columnar(value):
    keep = [i for i, c in enumerate(value['columns'])
            if not (c and any(term in c for term in PROTECTED_COLUMN_TERMS))]
    if len(keep) == len(value['columns']):
        return value
    return {
        'columns': [value['columns'][i] for i in keep],
        'rows': [[row[i] for i in keep] for row in value['rows']],
    }


def _columnar_json_bytes(value):
    return json.dumps(
        value, separators=(',', ':'),
        default=lambda o: o.isoformat() if hasattr(o, 'isoformat') else o,
    ).encode('utf-8')


def cache_ttl_for(request):
    return HEAVY_GEOGRAPHIC_CACHE_TTL if _is_heavy_geographic_url(request) else settings.CACHE_TTL


def _unauthenticated_key(cache_key):
    if cache_key.endswith(AUTHENTICATED_KEY_SUFFIX):
        return cache_key[:-len(AUTHENTICATED_KEY_SUFFIX)]
    return cache_key


def store_columnar_variants(request, cache_key, rows):
    """Cache columnar variants of `rows`; return JSON bytes for this request.

    The authenticated key gets the full columns; the unauthenticated key always
    gets protected columns removed (rows here may be unscrubbed).
    """
    if not isinstance(rows, list):
        return None
    value = to_columnar(rows)
    ttl = cache_ttl_for(request)
    public_bytes = _columnar_json_bytes(scrub_columnar(value))
    variants = [(_unauthenticated_key(cache_key) + COLUMNAR_KEY_SUFFIX, public_bytes)]
    own_bytes = public_bytes
    if cache_key.endswith(AUTHENTICATED_KEY_SUFFIX):
        own_bytes = _columnar_json_bytes(value)
        variants.append((cache_key + COLUMNAR_KEY_SUFFIX, own_bytes))
    for key, raw in variants:
        compressed = gzip.compress(raw)
        if len(compressed) > MAX_CACHE_VALUE_BYTES:
            logger.warning('Refusing to cache %s: compressed size %d bytes', key, len(compressed))
            continue
        cache.set(key, compressed, timeout=ttl)
    return own_bytes


def _json_bytes_response(view, request, raw):
    return view.finalize_response(request, HttpResponse(raw, content_type='application/json'))


def cache_request_path():
    def cache_decorator(function):
        @wraps(function)
        def cached_view(*original_args, **original_kwargs):
            view = original_args[0]
            request = original_args[1]
            params = deepcopy(request.query_params)
            # `shape` never enters the key (see columnar notes above).
            wants_columnar = params.pop(SHAPE_PARAM, [None])[-1] == COLUMNAR_SHAPE
            cache_key = construct_cache_key(request, params)
            columnar = (wants_columnar and is_columnar_eligible(request)
                        and has_cachable_format(request))

            # User must be logged in and trusted to view protected sets
            if not is_authenticated(request) and 'q' in params and ('lispenden' in params['q'] or 'foreclosure' in params['q'] or 'ocahousingcourt' in params['q']):
                return original_args[0].finalize_response(request, Response({'detail': 'Please login and request access to view results'}, status=status.HTTP_401_UNAUTHORIZED))

            if columnar:
                cached_columnar = cache.get(cache_key + COLUMNAR_KEY_SUFFIX)
                if cached_columnar is not None:
                    logger.debug('Serving columnar cache: {}'.format(cache_key))
                    return _json_bytes_response(view, request, gzip.decompress(cached_columnar))
                cached_rows = cache.get(cache_key)
                if cached_rows is not None:
                    raw = store_columnar_variants(request, cache_key, decompress_cache(cached_rows))
                    if raw is not None:
                        return _json_bytes_response(view, request, raw)

            # Single Redis GET (was: EXISTS then GET → 2 round-trips per hit).
            # `has_cachable_format` is cheap and gates the GET so we don't
            # round-trip for uncacheable formats.
            cached_value = cache.get(cache_key) if has_cachable_format(request) else None
            if cached_value is not None:
                logger.debug('Serving cache: {}'.format(cache_key))
                cached_value = decompress_cache(cached_value)
                cached_value = scrub_authenticated(cached_value, request)
                return original_args[0].finalize_response(request, Response(cached_value))
            else:
                response = function(*original_args, **original_kwargs)

                # only cache good JSON responses
                if (response.status_code == 200) and has_cachable_format(request):
                    value_to_cache = response.data
                    value_to_cache = scrub_pagination(value_to_cache)
                    value_to_cache = compress_cache(value_to_cache)

                    if len(value_to_cache) > MAX_CACHE_VALUE_BYTES:
                        # Don't bloat Redis with single huge responses; log so we
                        # can identify endpoints that produce them.
                        logger.warning(
                            'Refusing to cache %s: compressed size %d bytes > %d limit',
                            cache_key, len(value_to_cache), MAX_CACHE_VALUE_BYTES,
                        )
                    else:
                        # Heavy borough-wide / citywide /properties/ aggregates
                        # change very slowly (PLUTO is quarterly, RS annual,
                        # daily updates only nudge counts) and they're
                        # expensive to recompute (BK 5+ min cold), so give
                        # them a longer TTL than the default 24h. The weekly
                        # Sunday pre-warm refreshes them; structural-dataset
                        # update hooks invalidate explicitly when needed.
                        if _is_heavy_geographic_url(request):
                            ttl = HEAVY_GEOGRAPHIC_CACHE_TTL
                        else:
                            ttl = settings.CACHE_TTL
                        logger.debug('Caching: {} (ttl=%ss)'.format(cache_key), ttl)
                        cache.set(cache_key, value_to_cache, timeout=ttl)
                        if '__authenticated' in cache_key:  # also cache the scrubbed response for unauthenticated requests
                            scrubbed_cache_key = cache_key.replace('__authenticated', '')
                            logger.debug(
                                'Caching scrubbed varient: {}'.format(scrubbed_cache_key))
                            cache.set(scrubbed_cache_key, value_to_cache,
                                      timeout=ttl)

                    # Keep a columnar variant next to every fresh dashboard
                    # summary so the pre-warm covers columnar clients too.
                    columnar_raw = None
                    if is_columnar_eligible(request):
                        columnar_raw = store_columnar_variants(
                            request, cache_key, scrub_pagination(response.data))
                    if columnar and columnar_raw is not None:
                        return _json_bytes_response(view, request, columnar_raw)

                    logger.debug('Serving response: {}'.format(cache_key))
                    scrubbed_response = scrub_pagination(response.data)
                    scrubbed_response = scrub_authenticated(
                        scrubbed_response, request)
                    return original_args[0].finalize_response(request, Response(scrubbed_response))
                else:
                    return response
        return cached_view
    return cache_decorator
