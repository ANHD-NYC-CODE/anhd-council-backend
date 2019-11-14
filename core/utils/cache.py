import os
import time

import requests
import logging
logger = logging.getLogger('app')
import datetime
import base64
from datasets.utils import dates
from django.conf import settings


def create_async_cache_workers(token):
    from core.tasks import async_cache_council_property_summaries_full, async_cache_community_property_summaries_full, async_cache_stateassembly_property_summaries_full, async_cache_statesenate_property_summaries_full, async_cache_zipcode_property_summaries_full

    async_cache_council_property_summaries_full.delay(token)
    async_cache_community_property_summaries_full.delay(token)
    async_cache_stateassembly_property_summaries_full.delay(token)
    async_cache_statesenate_property_summaries_full.delay(token)
    async_cache_zipcode_property_summaries_full.delay(token)

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
