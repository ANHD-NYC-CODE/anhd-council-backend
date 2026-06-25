from datasets.utils import dates
from django.conf import settings
import os
import time
import requests
import logging
import datetime
import base64
logger = logging.getLogger('app')


def create_async_cache_workers(token):
    from core.tasks import (
        async_cache_council_property_summaries_full,
        async_cache_community_property_summaries_full,
        async_cache_stateassembly_property_summaries_full,
        async_cache_statesenate_property_summaries_full,
        async_cache_zipcode_property_summaries_full,
        async_cache_borough_property_summaries_full,
        async_cache_citywide_property_summaries_full,
    )

    async_cache_council_property_summaries_full.delay(token)
    async_cache_community_property_summaries_full.delay(token)
    async_cache_stateassembly_property_summaries_full.delay(token)
    async_cache_statesenate_property_summaries_full.delay(token)
    async_cache_zipcode_property_summaries_full.delay(token)
    # Added 2026-06-25: borough + citywide pre-warm so the "browse all of
    # Brooklyn / Manhattan / NYC" path doesn't hit a cold ~10 min SQL on
    # every first request. Queued same as the others — celery_default
    # processes them in turn so the load is naturally serialized.
    async_cache_borough_property_summaries_full.delay(token)
    async_cache_citywide_property_summaries_full.delay(token)

    logger.debug('Async caching started')


def cache_council_property_summaries_full(token, sleep=2, start=0):
    from datasets.models import Council
    # token = settings.CACHE_REQUEST_KEY

    headers = {"whoisit": token}
    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    # cache 1 month
    for record in Council.objects.all().order_by('pk')[start:]:
        try:
            logger.debug("Caching full Council: {}".format(record.pk))
            path = '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(
                record.pk)
            requests.get(
                root_url + path, headers=headers)
            time.sleep(sleep)
        except Exception as e:
            time.sleep(60)
            requests.get(
                root_url + path, headers=headers)

    logger.debug("Authenticated! Council month Pre-Caching complete!")


def cache_community_property_summaries_full(token, sleep=2, start=0):
    from datasets.models import Community
    # token = settings.CACHE_REQUEST_KEY

    headers = {"whoisit": token}

    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for record in Community.objects.all().order_by('pk')[start:]:
        try:
            logger.debug("Caching full Community: {}".format(record.pk))
            path = '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(
                record.pk)
            requests.get(
                root_url + path, headers=headers)
            time.sleep(sleep)
        except Exception as e:
            time.sleep(60)
            logger.debug("Caching full Community: {}".format(record.pk))
            requests.get(
                root_url + path, headers=headers)

    logger.debug("Authenticated Community month Pre-Caching complete!")


def cache_stateassembly_property_summaries_full(token, sleep=2, start=0):
    from datasets.models import StateAssembly
    # token = settings.CACHE_REQUEST_KEY

    headers = {"whoisit": token}

    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for record in StateAssembly.objects.all().order_by('pk')[start:]:
        try:
            logger.debug("Caching full StateAssembly: {}".format(record.pk))
            path = '/stateassemblies/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(
                record.pk)
            requests.get(
                root_url + path, headers=headers)
            time.sleep(sleep)
        except Exception as e:
            time.sleep(60)
            logger.debug("Caching full StateAssembly: {}".format(record.pk))
            requests.get(
                root_url + path, headers=headers)

    logger.debug("Authenticated StateAssembly month Pre-Caching complete!")


def cache_statesenate_property_summaries_full(token, sleep=2, start=0):
    from datasets.models import StateSenate
    # token = settings.CACHE_REQUEST_KEY

    headers = {"whoisit": token}

    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for record in StateSenate.objects.all().order_by('pk')[start:]:
        try:
            logger.debug("Caching full StateSenate: {}".format(record.pk))
            path = '/statesenates/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(
                record.pk)
            requests.get(
                root_url + path, headers=headers)
            time.sleep(sleep)
        except Exception as e:
            time.sleep(60)
            logger.debug("Caching full StateSenate: {}".format(record.pk))
            requests.get(
                root_url + path, headers=headers)

    logger.debug("Authenticated StateSenate month Pre-Caching complete!")


def cache_zipcode_property_summaries_full(token, sleep=1, start=0):
    from datasets.models import ZipCode
    # token = settings.CACHE_REQUEST_KEY

    headers = {"whoisit": token}

    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for record in ZipCode.objects.all().order_by('pk')[start:]:
        try:
            logger.debug("Caching full ZipCode: {}".format(record.pk))
            path = '/zipcodes/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(
                record.pk)
            requests.get(
                root_url + path, headers=headers)
            time.sleep(sleep)
        except Exception as e:
            time.sleep(60)
            logger.debug("Caching full ZipCode: {}".format(record.pk))
            requests.get(
                root_url + path, headers=headers)

    logger.debug("Authenticated ZipCode month Pre-Caching complete!")


# Borough pre-warm: just the 5 borough codes, no DB lookup needed.
# Each request can be slow (Brooklyn has the largest property set ~300K
# rows). Use longer sleep between calls and a longer request timeout so we
# don't pile workers if one of them takes ~10 min. Total runtime expected
# ~5-25 min depending on prod load.
def cache_borough_property_summaries_full(token, sleep=5):
    headers = {"whoisit": token}
    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for borough in ('MN', 'BK', 'BX', 'QN', 'SI'):
        try:
            logger.debug("Caching full Borough: %s", borough)
            path = ('/properties/?format=json&summary=true&summary-type=short-annotated'
                    '&annotation__start=full&unitsres__gte=1&borough={}').format(borough)
            requests.get(root_url + path, headers=headers, timeout=900)
            time.sleep(sleep)
        except Exception as e:
            logger.warning("Borough pre-warm failed for %s: %s", borough, e)
            time.sleep(60)

    logger.debug("Borough Pre-Caching complete!")


# Citywide pre-warm: a single (large) request. Response may exceed the
# 5 MB compressed MAX_CACHE_VALUE_BYTES cap; cache.py will log + skip the
# write in that case, but the connection still warms upstream-side query
# plans. Cheap to attempt — one request — and pays off when it fits.
def cache_citywide_property_summaries_full(token):
    headers = {"whoisit": token}
    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'
    path = ('/properties/?format=json&summary=true&summary-type=short-annotated'
            '&annotation__start=full&unitsres__gte=1')
    try:
        logger.debug("Caching full Citywide")
        requests.get(root_url + path, headers=headers, timeout=900)
    except Exception as e:
        logger.warning("Citywide pre-warm failed: %s", e)

    logger.debug("Citywide Pre-Caching complete!")
