"""Async custom-search jobs with pollable progress (Celery + Redis).

Flow: POST start -> Celery task calls the origin list endpoint (same code path,
same cache) -> poll returns progress, then inline results or `refetch`.

The worker request uses the internal `whoisit` header, so the origin treats it
as trusted (unscrubbed protected fields) and exempt from throttling and the
list-view concurrency limit. To compensate:
  * the worker takes a concurrency slot itself (waiting in a queue instead of
    getting a 503), so jobs and direct GETs share CUSTOM_SEARCH_MAX_CONCURRENT;
  * the start view enforces the protected-dataset login gate, and the poll view
    scrubs protected fields for untrusted pollers.
"""

import logging
import threading
import time
import uuid

import requests
from django.conf import settings
from django.core.cache import cache

from core.custom_search_concurrency import acquire_slot_blocking, release_slot

logger = logging.getLogger('app')

JOB_PREFIX = 'custom_search:job:'
JOB_TTL = 3600
DEFAULT_ORIGIN = 'http://app:8000'


def _job_key(job_id):
    return JOB_PREFIX + job_id


def set_job_state(job_id, **fields):
    state = cache.get(_job_key(job_id)) or {}
    state.update(fields)
    cache.set(_job_key(job_id), state, timeout=JOB_TTL)
    return state


def get_job_state(job_id):
    return cache.get(_job_key(job_id))


def create_custom_search_job(path, query_params):
    job_id = str(uuid.uuid4())
    set_job_state(
        job_id,
        status='queued',
        percent=0,
        phase='queued',
        path=path,
        query_params=dict(query_params),
    )
    from core.tasks import async_run_custom_search_job
    async_run_custom_search_job.delay(job_id)
    return job_id


def _is_finished(state):
    return not state or state.get('status') in ('complete', 'failed', 'cancelled')


def heartbeat_percent(elapsed_seconds, tau=60.0):
    """Estimated progress while SQL runs (no real progress signal exists).

    Eases from 20 toward 95 (~60% of the way after 1 min, ~95% after 3 min) so
    the bar keeps moving on multi-minute borough queries instead of freezing.
    """
    import math
    return min(95, int(20 + 75 * (1 - math.exp(-elapsed_seconds / tau))))


def _progress_heartbeat(job_id, stop_event):
    started = time.monotonic()
    while not stop_event.wait(2.0):
        if _is_finished(get_job_state(job_id)):
            return
        set_job_state(job_id, percent=heartbeat_percent(time.monotonic() - started), phase='querying')


def _origin():
    origin = getattr(settings, 'CUSTOM_SEARCH_JOB_ORIGIN', None) or getattr(
        settings, 'INTERNAL_API_ORIGIN', DEFAULT_ORIGIN)
    return origin.rstrip('/')


def _fetch(job_id, path, query_params):
    token = getattr(settings, 'CACHE_REQUEST_KEY', '')
    headers = {'whoisit': token} if token else {}
    set_job_state(job_id, status='running', percent=20, phase='querying')
    stop = threading.Event()
    heartbeat = threading.Thread(
        target=_progress_heartbeat, args=(job_id, stop), name=f'cs-job-{job_id[:8]}', daemon=True
    )
    heartbeat.start()
    try:
        return requests.get(
            _origin() + path,
            params={**query_params, 'format': 'json'},
            headers=headers,
            timeout=int(getattr(settings, 'CUSTOM_SEARCH_JOB_TIMEOUT', 540)),
        )
    finally:
        stop.set()
        heartbeat.join(timeout=3)


def _fail(job_id, error, http_status=None):
    set_job_state(
        job_id, status='failed', percent=100, phase='failed', http_status=http_status, error=error
    )


def run_custom_search_job(job_id):
    state = get_job_state(job_id)
    if _is_finished(state):  # missing, or cancelled before a worker picked it up
        return
    path = state.get('path') or '/properties/'
    query_params = state.get('query_params') or {}

    set_job_state(job_id, status='running', percent=5, phase='waiting')
    wait_timeout = int(getattr(settings, 'CUSTOM_SEARCH_JOB_SLOT_WAIT', 120))
    if not acquire_slot_blocking(wait_timeout):
        from datasets.views.property_views import CUSTOM_SEARCH_BUSY_DETAIL
        _fail(job_id, CUSTOM_SEARCH_BUSY_DETAIL, http_status=503)
        return

    try:
        if _is_finished(get_job_state(job_id)):  # cancelled while waiting
            return
        response = _fetch(job_id, path, query_params)
    except Exception as exc:
        logger.exception('custom_search job %s failed', job_id)
        _fail(job_id, str(exc))
        return
    finally:
        release_slot()

    if response.status_code != 200:
        try:
            detail = response.json().get('detail')
        except Exception:
            detail = response.text[:500] if response.text else None
        _fail(job_id, detail or f'HTTP {response.status_code}', http_status=response.status_code)
        return

    max_inline = int(getattr(settings, 'CUSTOM_SEARCH_JOB_MAX_INLINE_BYTES', 5 * 1024 * 1024))
    data = None
    if len(response.content) <= max_inline:
        try:
            data = response.json()
        except ValueError:
            data = None
    set_job_state(
        job_id, status='complete', percent=100, phase='complete', http_status=200, result=data
    )
