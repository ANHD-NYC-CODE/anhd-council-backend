"""Limit concurrent in-flight custom-search property list queries."""

import logging
import time
from contextlib import contextmanager

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('app')

SLOT_KEY = 'custom_search:in_flight'
DEFAULT_MAX = 3


def _max_slots():
    return int(getattr(settings, 'CUSTOM_SEARCH_MAX_CONCURRENT', DEFAULT_MAX))


def _redis_client():
    return cache.client.get_client(write=True)


def try_acquire_slot():
    """Return True if a slot was taken (caller must release_slot()), else False.

    Fails open (returns True, nothing to release) when Redis is unavailable;
    in that case release_slot() is still safe to call.
    """
    try:
        client = _redis_client()
        key = cache.client.make_key(SLOT_KEY)
        count = client.incr(key)
        client.expire(key, 3600)
    except Exception as exc:
        logger.warning('custom_search concurrency incr failed: %s', exc)
        return True

    if count > _max_slots():
        try:
            client.decr(key)
        except Exception:
            pass
        return False
    return True


def release_slot():
    try:
        client = _redis_client()
        key = cache.client.make_key(SLOT_KEY)
        remaining = client.decr(key)
        if remaining is not None and remaining < 0:
            client.set(key, 0)
    except Exception as exc:
        logger.warning('custom_search concurrency decr failed: %s', exc)


def acquire_slot_blocking(timeout, poll_interval=2.0, on_wait=None):
    """Wait up to `timeout` seconds for a slot. Returns True if acquired."""
    deadline = time.monotonic() + timeout
    while True:
        if try_acquire_slot():
            return True
        if time.monotonic() >= deadline:
            return False
        if on_wait:
            on_wait()
        time.sleep(poll_interval)


@contextmanager
def custom_search_concurrency_slot():
    """Acquire a slot for one custom-search list request; yields False if at capacity."""
    if not try_acquire_slot():
        yield False
        return
    try:
        yield True
    finally:
        release_slot()
