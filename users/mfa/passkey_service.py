import base64
import json

from django.conf import settings
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from users.mfa import challenge as mfa_challenge
from users.models import CustomUser, PasskeyCredential


def _webauthn_config():
    cfg = getattr(settings, 'WEBAUTHN', {})
    allowed = cfg.get('ALLOWED_ORIGINS') or [cfg.get('ORIGIN', 'http://localhost:3000')]
    return {
        'rp_id': cfg.get('RP_ID', 'localhost'),
        'rp_name': cfg.get('RP_NAME', 'Displacement Alert Project'),
        'origin': cfg.get('ORIGIN', 'http://localhost:3000'),
        'allowed_origins': allowed,
    }


def allowed_webauthn_origins():
    return _webauthn_config()['allowed_origins']


def _normalize_origin(origin):
    return origin.rstrip('/')


def resolve_webauthn_origin(origin=None, request=None):
    """Pick and validate the browser origin for a passkey ceremony."""
    cfg = _webauthn_config()
    allowed = {_normalize_origin(o) for o in cfg['allowed_origins']}

    candidates = []
    if origin:
        candidates.append(origin)
    if request is not None:
        header_origin = request.META.get('HTTP_ORIGIN')
        if header_origin:
            candidates.append(header_origin)
        candidates.append(f'{request.scheme}://{request.get_host()}')

    for candidate in candidates:
        if not candidate:
            continue
        normalized = _normalize_origin(candidate)
        if normalized in allowed:
            return normalized

    raise ValueError('WebAuthn origin is not allowed for this environment.')


def _expected_origin(origin=None, request=None):
    if origin is not None or request is not None:
        return resolve_webauthn_origin(origin=origin, request=request)
    return _normalize_origin(_webauthn_config()['origin'])


def _user_entity(user):
    cfg = _webauthn_config()
    return {
        'id': str(user.pk),
        'name': user.email or user.username,
        'display_name': user.get_full_name() or user.username,
    }


def begin_registration(user, scope_key):
    cfg = _webauthn_config()
    existing = PasskeyCredential.objects.filter(user=user)
    exclude = [
        PublicKeyCredentialDescriptor(id=base64url_to_bytes(c.credential_id))
        for c in existing
    ]
    options = generate_registration_options(
        rp_id=cfg['rp_id'],
        rp_name=cfg['rp_name'],
        user=_user_entity(user),
        exclude_credentials=exclude,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )
    mfa_challenge.store_webauthn_challenge(scope_key, options.challenge)
    return json.loads(options.model_dump_json())


def complete_registration(user, scope_key, credential_json, name='Passkey', *, origin=None, request=None):
    cfg = _webauthn_config()
    expected_origin = _expected_origin(origin=origin, request=request)
    expected_challenge = mfa_challenge.pop_webauthn_challenge(scope_key)
    if expected_challenge is None:
        raise ValueError('Registration challenge expired or missing')

    verification = verify_registration_response(
        credential=credential_json,
        expected_challenge=expected_challenge,
        expected_rp_id=cfg['rp_id'],
        expected_origin=expected_origin,
        require_user_verification=False,
    )

    credential_id = bytes_to_base64url(verification.credential_id)
    if PasskeyCredential.objects.filter(credential_id=credential_id).exists():
        raise ValueError('Passkey already registered')

    PasskeyCredential.objects.create(
        user=user,
        credential_id=credential_id,
        public_key=bytes_to_base64url(verification.credential_public_key),
        sign_count=verification.sign_count,
        name=name or 'Passkey',
    )
    return credential_id


def begin_authentication(user, challenge_id):
    cfg = _webauthn_config()
    credentials = PasskeyCredential.objects.filter(user=user)
    if not credentials.exists():
        raise ValueError('No passkeys registered')

    allow_credentials = [
        PublicKeyCredentialDescriptor(id=base64url_to_bytes(c.credential_id))
        for c in credentials
    ]
    options = generate_authentication_options(
        rp_id=cfg['rp_id'],
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    scope_key = f'auth:{challenge_id}'
    mfa_challenge.store_webauthn_challenge(scope_key, options.challenge)
    return json.loads(options.model_dump_json())


def complete_authentication(user, challenge_id, credential_json, *, origin=None, request=None):
    cfg = _webauthn_config()
    expected_origin = _expected_origin(origin=origin, request=request)
    scope_key = f'auth:{challenge_id}'
    expected_challenge = mfa_challenge.pop_webauthn_challenge(scope_key)
    if expected_challenge is None:
        raise ValueError('Authentication challenge expired or missing')

    credential_id = credential_json.get('id') or credential_json.get('rawId')
    if not credential_id:
        raise ValueError('Missing credential id')

    if isinstance(credential_id, str):
        credential_id_b64 = credential_id
    else:
        credential_id_b64 = bytes_to_base64url(credential_id)

    stored = PasskeyCredential.objects.filter(user=user, credential_id=credential_id_b64).first()
    if not stored:
        raise ValueError('Unknown passkey')

    verification = verify_authentication_response(
        credential=credential_json,
        expected_challenge=expected_challenge,
        expected_rp_id=cfg['rp_id'],
        expected_origin=expected_origin,
        credential_public_key=base64url_to_bytes(stored.public_key),
        credential_current_sign_count=stored.sign_count,
        require_user_verification=False,
    )

    stored.sign_count = verification.new_sign_count
    stored.save(update_fields=['sign_count'])
    return stored.credential_id
