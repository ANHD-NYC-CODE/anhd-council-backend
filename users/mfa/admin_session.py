from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse

ADMIN_MFA_USER_ID = 'admin_mfa_user_id'
ADMIN_MFA_CHALLENGE_ID = 'admin_mfa_challenge_id'
ADMIN_MFA_ENROLLMENT_TOKEN = 'admin_mfa_enrollment_token'
ADMIN_MFA_VERIFIED = 'admin_mfa_verified'


def webauthn_origin(request):
    return f'{request.scheme}://{request.get_host()}'


def clear_admin_mfa_session(request):
    for key in (
        ADMIN_MFA_USER_ID,
        ADMIN_MFA_CHALLENGE_ID,
        ADMIN_MFA_ENROLLMENT_TOKEN,
    ):
        request.session.pop(key, None)


def pending_admin_mfa_user(request):
    from users.models import CustomUser

    user_id = request.session.get(ADMIN_MFA_USER_ID)
    if not user_id:
        return None
    user = CustomUser.objects.filter(pk=user_id, is_active=True).first()
    if user and user.is_mfa_required_role():
        return user
    return None


def finish_admin_login(request, user):
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    request.session[ADMIN_MFA_VERIFIED] = True
    clear_admin_mfa_session(request)
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(reverse('admin:index'))
