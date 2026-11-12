"""Celery dead-man monitoring: workers record a heartbeat; HTTP checks freshness."""

from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def heartbeat_cache_key():
    return getattr(settings, 'CELERY_HEARTBEAT_CACHE_KEY', 'celery_heartbeat')


def heartbeat_max_age_seconds():
    return int(getattr(settings, 'CELERY_HEARTBEAT_MAX_AGE_SECONDS', 900))


def record_celery_heartbeat():
    """Called from a Celery worker after beat schedules the heartbeat task."""
    now = timezone.now()
    ttl = heartbeat_max_age_seconds() * 3
    cache.set(heartbeat_cache_key(), now.isoformat(), timeout=ttl)
    return now


def _parse_heartbeat(raw):
    if not raw:
        return None
    if isinstance(raw, datetime):
        if timezone.is_naive(raw):
            return timezone.make_aware(raw, timezone.get_current_timezone())
        return raw
    try:
        parsed = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def evaluate_celery_heartbeat():
    """Return status dict for the /health/celery/ endpoint."""
    max_age = heartbeat_max_age_seconds()
    last_seen = _parse_heartbeat(cache.get(heartbeat_cache_key()))
    now = timezone.now()

    if last_seen is None:
        return {
            'ok': False,
            'reason': 'no_heartbeat',
            'last_seen': None,
            'age_seconds': None,
            'max_age_seconds': max_age,
        }

    age_seconds = (now - last_seen).total_seconds()
    stale = age_seconds > max_age
    return {
        'ok': not stale,
        'reason': 'stale' if stale else 'ok',
        'last_seen': last_seen.isoformat(),
        'age_seconds': int(age_seconds),
        'max_age_seconds': max_age,
    }
