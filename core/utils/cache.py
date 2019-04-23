import requests
import logging

logger = logging.getLogger('app')
import datetime
from dateutil.relativedelta import relativedelta


def create_async_cache_workers():
    from core.tasks import async_cache_council_property_summaries, async_cache_community_property_summaries
    async_cache_council_property_summaries.delay()
    async_cache_community_property_summaries.delay()
    logger.debug('Async caching started')


def cache_council_property_summaries():
    from datasets.models import Council
    today = datetime.datetime.today()
    one_month_ago = (today.replace(day=1) - relativedelta(months=1)).strftime('%m/%d/%Y')
    one_year_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%m/%d/%Y')
    three_years_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%m/%d/%Y')

    # cache 1 month
    for record in Council.objects.all():
        print("Caching Council: {}".format(record.pk))
        logger.debug("Caching Council: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    # cache 1 year
    for record in Council.objects.all():
        print("Caching Council: {}".format(record.pk))
        logger.debug("Caching Council: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    # cache 3 year
    for record in Council.objects.all():
        print("Caching Council: {}".format(record.pk))
        logger.debug("Caching Council: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))
    print("Council Pre-Caching complete!")
    logger.debug("Council Pre-Caching complete!")


def cache_community_property_summaries():
    from datasets.models import Community
    today = datetime.datetime.today()
    one_month_ago = (today.replace(day=1) - relativedelta(months=1)).strftime('%m/%d/%Y')
    one_year_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%m/%d/%Y')
    three_years_ago = (today.replace(day=1) - relativedelta(years=1)).strftime('%m/%d/%Y')

    for record in Community.objects.all():
        print("Caching Community: {}".format(record.pk))
        logger.debug("Caching Community: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_month_ago))

    # cache 1 year
    for record in Community.objects.all():
        print("Caching Community: {}".format(record.pk))
        logger.debug("Caching Community: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, one_year_ago))

    # cache 3 year
    for record in Community.objects.all():
        print("Caching Community: {}".format(record.pk))
        logger.debug("Caching Community: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short-annotated&annotation__start={}&unitsres__gte=1'.format(record.pk, three_years_ago))

    print("Community Pre-Caching complete!")
    logger.debug("Community Pre-Caching complete!")
