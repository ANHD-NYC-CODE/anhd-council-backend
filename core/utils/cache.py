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
    from core.tasks import async_cache_council_property_summaries_month, async_cache_community_property_summaries_month, async_cache_council_property_summaries_year, async_cache_community_property_summaries_year, async_cache_council_property_summaries_3_year, async_cache_community_property_summaries_3_year

    async_cache_council_property_summaries_month.delay()
    async_cache_community_property_summaries_month.delay()
    async_cache_council_property_summaries_year.delay()
    async_cache_community_property_summaries_year.delay()
    async_cache_council_property_summaries_3_year.delay()
    async_cache_community_property_summaries_3_year.delay()
    logger.debug('Async caching started')


def cache_council_property_summaries_month():
    from datasets.models import Council
    today = datetime.datetime.today()
    one_month_ago = dates.get_last_month(string=True)

    # cache 1 month
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago), headers=headers)

    logger.debug("Authenticated! Council month Pre-Caching complete!")

    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    logger.debug("Unauthenticated! Council month Pre-Caching complete!")


def cache_council_property_summaries_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    one_year_ago = dates.get_last_year(string=True)

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago), headers=headers)

    logger.debug("Authenticated Council 1-year Pre-Caching complete!")

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Unauthenticated Council 1-year Pre-Caching complete!")


def cache_council_property_summaries_3_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    three_years_ago = dates.get_last_3years(string=True)

    # cache 3 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago), headers=headers)

    logger.debug("Authenticated Council 3-year Pre-Caching complete!")

    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))

    logger.debug("Unauthenticated Council 3-year Pre-Caching complete!")


def cache_community_property_summaries_month():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_month_ago = dates.get_last_month(string=True)

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago), headers=headers)

    logger.debug("Authenticated Community month Pre-Caching complete!")

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    logger.debug("Unauthenticated Community month Pre-Caching complete!")


def cache_community_property_summaries_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_year_ago = dates.get_last_year(string=True)

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago), headers=headers)

    logger.debug("Authenticated Community 1 year Pre-Caching complete!")

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Unauthentcated Community 1 year Pre-Caching complete!")


def cache_community_property_summaries_3_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    three_years_ago = dates.get_last_3years(string=True)

    # cache 3 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago), headers=headers)

    logger.debug("Authenticated Community 3 year Pre-Caching complete!")

    # cache 3 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))

    logger.debug("Unauthenticated Community 3 year Pre-Caching complete!")
