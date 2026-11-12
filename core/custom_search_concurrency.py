"""Limit concurrent in-flight custom-search property list queries.

Slots are members of a Redis sorted set scored by acquire time. A slot whose
holder died without releasing (gunicorn worker killed at --timeout, container
restart mid-search) is reaped once it is older than SLOT_STALE_SECONDS, so a
leak heals itself instead of 503-ing every search.
"""

import logging
import time
import uuid
from contextlib import contextmanager

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('app')

SLOT_KEY = 'custom_search:slots'
DEFAULT_MAX = 3
# Longest a slot can legitimately be held: gunicorn --timeout 600 (and the job
# worker's 540 s request timeout), plus margin.
SLOT_STALE_SECONDS = 700
# Returned when Redis is unavailable: the request runs (fail open) and release
# is a no-op, so it never frees someone else's slot.
FAIL_OPEN_TOKEN = 'fail-open'


def _max_slots():
    return int(getattr(settings, 'CUSTOM_SEARCH_MAX_CONCURRENT', DEFAULT_MAX))


def _redis():
    return cache.client.get_client(write=True), cache.client.make_key(SLOT_KEY)


def try_acquire_slot():
    """Return a slot token (pass it to release_slot), or None if at capacity."""
    try:
        client, key = _redis()
        now = time.time()
        token = uuid.uuid4().hex
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, '-inf', now - SLOT_STALE_SECONDS)
        pipe.zadd(key, {token: now})
        pipe.zcard(key)
        pipe.expire(key, SLOT_STALE_SECONDS)
        _, _, count, _ = pipe.execute()
    except Exception as exc:
        logger.warning('custom_search concurrency acquire failed: %s', exc)
        return FAIL_OPEN_TOKEN

    if count > _max_slots():
        release_slot(token)
        return None
    return token


def release_slot(token):
    if not token or token == FAIL_OPEN_TOKEN:
        return
    try:
        client, key = _redis()
        client.zrem(key, token)
    except Exception as exc:
        logger.warning('custom_search concurrency release failed: %s', exc)


def slots_in_use():
    try:
        client, key = _redis()
        client.zremrangebyscore(key, '-inf', time.time() - SLOT_STALE_SECONDS)
        return client.zcard(key)
    except Exception:
        return 0


@contextmanager
def custom_search_concurrency_slot():
    """Yields True while holding a slot, False if at capacity."""
    token = try_acquire_slot()
    if token is None:
        yield False
        return
    try:
        yield True
    finally:
        release_slot(token)
