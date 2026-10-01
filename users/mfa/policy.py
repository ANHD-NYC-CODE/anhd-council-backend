from django.conf import settings
from django.utils import timezone

from users.models import CustomUser, PasskeyCredential, UserTotpDevice


def mfa_enforcement_active(at=None):
    at = at or timezone.now()
    start = getattr(settings, 'MFA_STAFF_ENFORCEMENT_START', None)
    if start is None:
        return True
    if timezone.is_naive(start):
        start = timezone.make_aware(start)
    return at >= start


def mfa_staff_grace_deadline():
    start = getattr(settings, 'MFA_STAFF_ENFORCEMENT_START', None)
    if start is None:
        return None
    if timezone.is_naive(start):
        return timezone.make_aware(start)
    return start


def staff_in_mfa_grace_period(user):
    return (
        user.is_mfa_required_role()
        and not user_has_mfa_enabled(user)
        and not mfa_enforcement_active()
    )


def user_has_confirmed_totp(user):
    return UserTotpDevice.objects.filter(user=user, confirmed=True).exists()


def user_has_passkeys(user):
    return PasskeyCredential.objects.filter(user=user).exists()


def user_has_mfa_enabled(user):
    return user_has_confirmed_totp(user) or user_has_passkeys(user)


def user_requires_mfa_enrollment(user):
    if not user.is_mfa_required_role() or user_has_mfa_enabled(user):
        return False
    return mfa_enforcement_active()


def available_mfa_methods(user):
    methods = []
    if user_has_confirmed_totp(user):
        methods.append('totp')
    if user_has_passkeys(user):
        methods.append('passkey')
    return methods


def login_step_after_password(user):
    """
    Returns one of: complete, mfa_required, enrollment_required
    """
    if user_requires_mfa_enrollment(user):
        return 'enrollment_required'
    if user_has_mfa_enabled(user):
        return 'mfa_required'
    return 'complete'


def passkey_revoke_allowed(user, passkey):
    """
    Staff must retain at least one MFA method (TOTP and/or another passkey).
    Optional MFA users may remove all passkeys.
    Returns (allowed: bool, detail: str | None).
    """
    if not user.is_mfa_required_role() or not mfa_enforcement_active():
        return True, None

    if user_has_confirmed_totp(user):
        return True, None

    remaining = PasskeyCredential.objects.filter(user=user).exclude(pk=passkey.pk).count()
    if remaining >= 1:
        return True, None

    return False, (
        'Admin accounts must keep at least one second factor. '
        'Enable an authenticator app or register another passkey before removing this one.'
    )
