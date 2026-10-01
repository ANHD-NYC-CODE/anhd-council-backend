import secrets
import uuid

from django.conf import settings
from django.core.cache import cache

MFA_CHALLENGE_PREFIX = 'mfa:challenge:'
ENROLLMENT_PREFIX = 'mfa:enrollment:'
WEBAUTHN_PREFIX = 'mfa:webauthn:'


def _challenge_ttl():
    return getattr(settings, 'MFA_CHALLENGE_TTL_SECONDS', 300)


def create_mfa_challenge(user_id):
    challenge_id = str(uuid.uuid4())
    cache.set(
        f'{MFA_CHALLENGE_PREFIX}{challenge_id}',
        {'user_id': user_id, 'kind': 'mfa'},
        timeout=_challenge_ttl(),
    )
    return challenge_id


def create_enrollment_session(user_id):
    token = secrets.token_urlsafe(32)
    cache.set(
        f'{ENROLLMENT_PREFIX}{token}',
        {'user_id': user_id},
        timeout=_challenge_ttl(),
    )
    return token


def get_mfa_challenge(challenge_id):
    return cache.get(f'{MFA_CHALLENGE_PREFIX}{challenge_id}')


def consume_mfa_challenge(challenge_id):
    key = f'{MFA_CHALLENGE_PREFIX}{challenge_id}'
    payload = cache.get(key)
    if payload:
        cache.delete(key)
    return payload


def get_enrollment_session(token):
    return cache.get(f'{ENROLLMENT_PREFIX}{token}')


def user_id_from_enrollment_or_challenge(*, challenge_id=None, enrollment_token=None):
    if enrollment_token:
        session = get_enrollment_session(enrollment_token)
        if session:
            return session['user_id']
    if challenge_id:
        session = get_mfa_challenge(challenge_id)
        if session:
            return session['user_id']
    return None


def store_webauthn_challenge(scope_key, challenge_bytes):
    cache.set(
        f'{WEBAUTHN_PREFIX}{scope_key}',
        challenge_bytes,
        timeout=_challenge_ttl(),
    )


def pop_webauthn_challenge(scope_key):
    key = f'{WEBAUTHN_PREFIX}{scope_key}'
    value = cache.get(key)
    if value is not None:
        cache.delete(key)
    return value
