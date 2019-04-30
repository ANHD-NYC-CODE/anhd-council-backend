import os

import requests
import logging
logger = logging.getLogger('app')
import datetime
import base64
from datasets.utils import dates
from django.conf import settings


def create_async_cache_workers():
    logger.debug('create: {}'.format(settings.CACHE_REQUEST_KEY))
    from core.tasks import async_cache_council_property_summaries_full, async_cache_community_property_summaries_full

    async_cache_council_property_summaries_full.delay()
    async_cache_community_property_summaries_full.delay()

    logger.debug('Async caching started')


def cache_council_property_summaries_full():
    from datasets.models import Council
    token = settings.CACHE_REQUEST_KEY
    logger.debug('t: {}'.format(token))
    headers = {"whoisit": token}
    logger.debug('h: {}'.format(headers))
    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    # cache 1 month
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching full Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated! Council month Pre-Caching complete!")


def cache_community_property_summaries_full():
    from datasets.models import Community
    token = settings.CACHE_REQUEST_KEY
    logger.debug('t: {}'.format(token))
    headers = {"whoisit": token}
    logger.debug('h: {}'.format(headers))
    root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching full Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Community month Pre-Caching complete!")
