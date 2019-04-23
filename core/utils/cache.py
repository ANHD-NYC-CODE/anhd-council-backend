import requests
import logging

logger = logging.getLogger('app')
import datetime
from dateutil.relativedelta import relativedelta


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
        print("Caching Council 1 month: {}".format(record.pk))
        logger.debug("Caching Council 1 month: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        print("Caching Council 1 year: {}".format(record.pk))
        logger.debug("Caching Council 1 year: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Council month Pre-Caching complete!")


def cache_council_property_summaries_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    one_year_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 1 year
    for record in Council.objects.all().order_by('pk'):
        print("Caching Council 1 year: {}".format(record.pk))
        logger.debug("Caching Council 1 year: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Council 1-year Pre-Caching complete!")


def cache_council_property_summaries_3_year():
    from datasets.models import Council
    today = datetime.datetime.today()
    three_years_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 3 year
    for record in Council.objects.all().order_by('pk'):
        print("Caching Council 3 years: {}".format(record.pk))
        logger.debug("Caching Council 3 years: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))

    logger.debug("Council 3-year Pre-Caching complete!")


def cache_community_property_summaries_month():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_month_ago = (today.replace(day=1) - relativedelta(months=1)).strftime('%Y-%m-%d')

    for record in Community.objects.all().order_by('pk'):
        print("Caching Community 1 month: {}".format(record.pk))
        logger.debug("Caching Community 1 month: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching Community 1 year: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Community month Pre-Caching complete!")


def cache_community_property_summaries_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_year_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 1 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching Community 1 year: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    logger.debug("Community 1 year Pre-Caching complete!")


def cache_community_property_summaries_3_year():
    from datasets.models import Community
    today = datetime.datetime.today()
    three_years_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%Y-%m-%d')

    # cache 3 year
    for record in Community.objects.all().order_by('pk'):
        logger.debug("Caching Community 3 years: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))

    logger.debug("Community 3 year Pre-Caching complete!")
