import os

import requests
import logging
logger = logging.getLogger('app')
import datetime
import base64
from datasets.utils import dates
from django.conf import settings
token = settings.CACHE_REQUEST_KEY
headers = {"whoisit": token}
root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'


def create_async_cache_workers():
    from core.tasks import async_cache_council_property_summaries_month, async_cache_community_property_summaries_month, async_cache_council_property_summaries_year, async_cache_community_property_summaries_year, async_cache_council_property_summaries_3_year, async_cache_community_property_summaries_3_year, async_cache_council_property_summaries_full


async_cache_community_property_summaries_full

    async_cache_council_property_summaries_full.delay()
    async_cache_community_property_summaries_full.delay()

    logger.debug('Async caching started')


def cache_council_property_summaries_full():
    from datasets.models import Council

    # cache 1 month
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching full Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated! Council month Pre-Caching complete!")


def cache_council_property_summaries_month():
    from datasets.models import Council

    # cache 1 month
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=recent&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated! Council month Pre-Caching complete!")


def cache_council_property_summaries_year():
    from datasets.models import Council

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=lastyear&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Council 1-year Pre-Caching complete!")


def cache_council_property_summaries_3_year():
    from datasets.models import Council

    # cache 3 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=last3years&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Council 3-year Pre-Caching complete!")


def cache_community_property_summaries_full():
    from datasets.models import Community

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching full Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=full&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Community month Pre-Caching complete!")


def cache_community_property_summaries_month():
    from datasets.models import Community

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=recent&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Community month Pre-Caching complete!")


def cache_community_property_summaries_year():
    from datasets.models import Community

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=lastyear&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Community 1 year Pre-Caching complete!")


def cache_community_property_summaries_3_year():
    from datasets.models import Community

    # cache 3 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start=last3years&unitsres__gte=1'.format(record.pk), headers=headers)

    logger.debug("Authenticated Community 3 year Pre-Caching complete!")
