import requests
from datasets import models as ds
import logging

logger = logging.getLogger('app')


from core.tasks import async_cache_council_property_summaries, async_cache_council_property_summaries


def create_async_cache_workers():
    async_cache_council_property_summaries.delay()
    async_cache_council_property_summaries.delay()
    logger.debug('Async caching complete!')


def cache_council_property_summaries():
    for record in ds.Council.objects.all():
        print("Caching Council: {}".format(record.pk))
        logger.debug("Caching Council: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/councils/{}/properties/?format=json&summary=true&summary-type=short'.format(record.pk))
    print("Council Pre-Caching complete!")
    logger.debug("Council Pre-Caching complete!")


def cache_community_property_summaries():

    for record in ds.Community.objects.all():
        print("Caching Community: {}".format(record.pk))
        logger.debug("Caching Community: {}".format(record.pk))
        requests.get(
            'https://api.displacementalert.org/communities/{}/properties/?format=json&summary=true&summary-type=short'.format(record.pk))

    print("Community Pre-Caching complete!")
    logger.debug("Community Pre-Caching complete!")
