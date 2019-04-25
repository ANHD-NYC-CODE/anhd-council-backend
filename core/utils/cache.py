import os

import requests
import logging
logger = logging.getLogger('app')
import datetime
from dateutil.relativedelta import relativedelta
import base64
from django.conf import settings
token = settings.CACHE_REQUEST_KEY
headers = {"whoisit": token}
root_url = 'http://localhost:8000' if settings.DEBUG else 'https://api.displacementalert.org'

logger.warning(headers)


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
    one_month_ago = (today.replace(day=1) - relativedelta(months=1)).strftime('%Y-%m-%d')

    # cache 1 month
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago), headers=headers)

    logger.debug("Council month Pre-Caching complete!")


def cache_council_property_summaries_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    one_year_ago = (today.replace(day=1).replace(month=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago), headers=headers)

    logger.debug("Council 1-year Pre-Caching complete!")


def cache_council_property_summaries_3_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    three_years_ago = (today.replace(day=1).replace(month=1) - relativedelta(years=3)).strftime('%Y-%m-%d')

    # cache 3 year
    for record in Council.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Council: {}".format(record.pk))
        requests.get(
            root_url + '/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago), headers=headers)

    logger.debug("Council 3-year Pre-Caching complete!")


def cache_community_property_summaries_month():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_month_ago = (today.replace(day=1) - relativedelta(months=3)).strftime('%Y-%m-%d')

    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-month Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago), headers=headers)

    logger.debug("Community month Pre-Caching complete!")


def cache_community_property_summaries_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_year_ago = (today.replace(day=1).replace(month=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 1-year Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago), headers=headers)

    logger.debug("Community 1 year Pre-Caching complete!")


def cache_community_property_summaries_3_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    three_years_ago = (today.replace(day=1).replace(month=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 3 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching 3-years Community: {}".format(record.pk))
        requests.get(
            root_url + '/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago), headers=headers)

    logger.debug("Community 3 year Pre-Caching complete!")
