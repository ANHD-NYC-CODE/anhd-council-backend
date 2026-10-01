import pyotp

from users.models import UserTotpDevice


def get_or_create_pending_totp(user):
    device, _created = UserTotpDevice.objects.get_or_create(
        user=user,
        defaults={'secret': pyotp.random_base32()},
    )
    if device.confirmed:
        return None
    if not device.secret:
        device.secret = pyotp.random_base32()
        device.save(update_fields=['secret'])
    return device


def provisioning_uri(device):
    issuer = 'Displacement Alert Project'
    totp = pyotp.TOTP(device.secret)
    return totp.provisioning_uri(name=device.user.email or device.user.username, issuer_name=issuer)


def verify_totp_code(user, code, *, require_confirmed=True):
    device = UserTotpDevice.objects.filter(user=user).first()
    if not device or not device.secret:
        return False
    if require_confirmed and not device.confirmed:
        return False
    totp = pyotp.TOTP(device.secret)
    return totp.verify(code, valid_window=1)


def confirm_totp_device(user, code):
    device = UserTotpDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        return False
    totp = pyotp.TOTP(device.secret)
    if not totp.verify(code, valid_window=1):
        return False
    device.confirmed = True
    device.save(update_fields=['confirmed'])
    return True
