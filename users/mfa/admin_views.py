import json

from django.contrib import messages
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from users.models import PasskeyCredential
from users.mfa import challenge as mfa_challenge
from users.mfa import passkey_service
from users.mfa import policy
from users.mfa import totp_service
from users.mfa.admin_session import (
    ADMIN_MFA_CHALLENGE_ID,
    ADMIN_MFA_ENROLLMENT_TOKEN,
    ADMIN_MFA_USER_ID,
    clear_admin_mfa_session,
    finish_admin_login,
    pending_admin_mfa_user,
)


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaLoginView(LoginView):
    template_name = 'admin/login.html'
    authentication_form = AdminAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('admin:index')

    def form_valid(self, form):
        user = form.get_user()
        step = policy.login_step_after_password(user)

        if step == 'complete':
            return finish_admin_login(self.request, user)

        if step == 'enrollment_required':
            token = mfa_challenge.create_enrollment_session(user.pk)
            self.request.session[ADMIN_MFA_USER_ID] = user.pk
            self.request.session[ADMIN_MFA_ENROLLMENT_TOKEN] = token
            return redirect('admin_mfa_enroll')

        challenge_id = mfa_challenge.create_mfa_challenge(user.pk)
        self.request.session[ADMIN_MFA_USER_ID] = user.pk
        self.request.session[ADMIN_MFA_CHALLENGE_ID] = challenge_id
        return redirect('admin_mfa_verify')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deadline = policy.mfa_staff_grace_deadline()
        if deadline and not policy.mfa_enforcement_active():
            context['mfa_grace_message'] = (
                f'Staff must enable two-factor authentication by '
                f'{deadline.strftime("%B %d, %Y")} ({deadline.tzname()}).'
            )
        return context


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaVerifyView(View):
    template_name = 'admin/mfa_verify.html'

    def get(self, request):
        user = pending_admin_mfa_user(request)
        challenge_id = request.session.get(ADMIN_MFA_CHALLENGE_ID)
        if not user or not challenge_id:
            return redirect('admin:login')
        if not mfa_challenge.get_mfa_challenge(challenge_id):
            clear_admin_mfa_session(request)
            messages.error(request, 'Verification session expired. Please sign in again.')
            return redirect('admin:login')
        return render(
            request,
            self.template_name,
            {
                'user': user,
                'methods': policy.available_mfa_methods(user),
                'next': request.GET.get('next', ''),
            },
        )

    def post(self, request):
        user = pending_admin_mfa_user(request)
        challenge_id = request.session.get(ADMIN_MFA_CHALLENGE_ID)
        code = request.POST.get('code', '').strip()
        if not user or not challenge_id or not code:
            messages.error(request, 'Invalid verification request.')
            return redirect('admin:login')
        if not totp_service.verify_totp_code(user, code):
            messages.error(request, 'Invalid authenticator code.')
            return redirect('admin_mfa_verify')
        mfa_challenge.consume_mfa_challenge(challenge_id)
        return finish_admin_login(request, user)


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaEnrollView(View):
    template_name = 'admin/mfa_enroll.html'

    def _enrollment_token(self, request):
        return request.session.get(ADMIN_MFA_ENROLLMENT_TOKEN)

    def get(self, request):
        user = pending_admin_mfa_user(request)
        token = self._enrollment_token(request)
        if not user or not token or not mfa_challenge.get_enrollment_session(token):
            return redirect('admin:login')
        device = totp_service.get_or_create_pending_totp(user)
        context = {
            'user': user,
            'deadline': policy.mfa_staff_grace_deadline(),
            'totp_secret': device.secret if device else None,
            'otpauth_url': totp_service.provisioning_uri(device) if device else None,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = pending_admin_mfa_user(request)
        token = self._enrollment_token(request)
        if not user or not token:
            return redirect('admin:login')
        code = request.POST.get('code', '').strip()
        if not code or not totp_service.confirm_totp_device(user, code):
            messages.error(request, 'Invalid verification code. Try again.')
            return redirect('admin_mfa_enroll')
        messages.success(request, 'Authenticator app enabled. You are signed in.')
        return finish_admin_login(request, user)


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaPasskeyAuthBeginView(View):
    def post(self, request):
        user = pending_admin_mfa_user(request)
        challenge_id = request.session.get(ADMIN_MFA_CHALLENGE_ID)
        if not user or not challenge_id:
            return JsonResponse({'detail': 'Session expired.'}, status=400)
        try:
            options = passkey_service.begin_authentication(user, challenge_id)
        except ValueError as exc:
            return JsonResponse({'detail': str(exc)}, status=400)
        return JsonResponse({'publicKey': options})


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaPasskeyAuthCompleteView(View):
    def post(self, request):
        user = pending_admin_mfa_user(request)
        challenge_id = request.session.get(ADMIN_MFA_CHALLENGE_ID)
        if not user or not challenge_id:
            return JsonResponse({'detail': 'Session expired.'}, status=400)
        try:
            credential = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid credential payload.'}, status=400)
        try:
            passkey_service.complete_authentication(
                user,
                challenge_id,
                credential,
                request=request,
            )
        except ValueError as exc:
            return JsonResponse({'detail': str(exc)}, status=401)
        mfa_challenge.consume_mfa_challenge(challenge_id)
        response = finish_admin_login(request, user)
        return JsonResponse({'redirect': response.url})


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaPasskeyRegisterBeginView(View):
    def post(self, request):
        user = pending_admin_mfa_user(request)
        token = request.session.get(ADMIN_MFA_ENROLLMENT_TOKEN)
        if not user or not token:
            return JsonResponse({'detail': 'Session expired.'}, status=400)
        scope_key = f'enroll:{token}'
        try:
            options = passkey_service.begin_registration(user, scope_key)
        except Exception as exc:
            return JsonResponse({'detail': str(exc)}, status=400)
        return JsonResponse({'publicKey': options})


@method_decorator(csrf_protect, name='dispatch')
class AdminMfaPasskeyRegisterCompleteView(View):
    def post(self, request):
        user = pending_admin_mfa_user(request)
        token = request.session.get(ADMIN_MFA_ENROLLMENT_TOKEN)
        if not user or not token:
            return JsonResponse({'detail': 'Session expired.'}, status=400)
        try:
            payload = json.loads(request.body)
            credential = payload.get('credential')
            name = payload.get('name') or 'Admin passkey'
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid payload.'}, status=400)
        scope_key = f'enroll:{token}'
        try:
            passkey_service.complete_registration(
                user,
                scope_key,
                credential,
                name=name,
                request=request,
            )
        except ValueError as exc:
            return JsonResponse({'detail': str(exc)}, status=400)
        messages.success(request, 'Passkey registered. You are signed in.')
        response = finish_admin_login(request, user)
        return JsonResponse({'redirect': response.url})


def _settings_scope_key(user):
    return f'user:{user.pk}'


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class AdminMfaSettingsView(View):
    template_name = 'admin/mfa_settings.html'

    def get(self, request):
        user = request.user
        totp_pending = None
        otpauth_url = None
        if not policy.user_has_confirmed_totp(user):
            device = totp_service.get_or_create_pending_totp(user)
            if device:
                totp_pending = device.secret
                otpauth_url = totp_service.provisioning_uri(device)
        passkeys = PasskeyCredential.objects.filter(user=user).order_by('-created_at')
        context = {
            'user': user,
            'totp_enabled': policy.user_has_confirmed_totp(user),
            'totp_secret': totp_pending,
            'otpauth_url': otpauth_url,
            'passkeys': passkeys,
            'deadline': policy.mfa_staff_grace_deadline(),
            'enforcement_active': policy.mfa_enforcement_active(),
            'mfa_setup_recommended': policy.staff_in_mfa_grace_period(user),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        code = request.POST.get('code', '').strip()
        if not code:
            messages.error(request, 'Enter a verification code.')
            return redirect('admin_mfa_settings')
        if policy.user_has_confirmed_totp(user):
            messages.info(request, 'Authenticator app is already enabled.')
            return redirect('admin_mfa_settings')
        if not totp_service.confirm_totp_device(user, code):
            messages.error(request, 'Invalid verification code. Try again.')
            return redirect('admin_mfa_settings')
        messages.success(request, 'Authenticator app enabled.')
        return redirect('admin_mfa_settings')


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class AdminMfaSettingsPasskeyRegisterBeginView(View):
    def post(self, request):
        user = request.user
        scope_key = _settings_scope_key(user)
        try:
            options = passkey_service.begin_registration(user, scope_key)
        except Exception as exc:
            return JsonResponse({'detail': str(exc)}, status=400)
        return JsonResponse({'publicKey': options})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class AdminMfaSettingsPasskeyRegisterCompleteView(View):
    def post(self, request):
        user = request.user
        try:
            payload = json.loads(request.body)
            credential = payload.get('credential')
            name = payload.get('name') or 'Admin passkey'
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid payload.'}, status=400)
        scope_key = _settings_scope_key(user)
        try:
            passkey_service.complete_registration(
                user,
                scope_key,
                credential,
                name=name,
                request=request,
            )
        except ValueError as exc:
            return JsonResponse({'detail': str(exc)}, status=400)
        messages.success(request, 'Passkey registered.')
        return JsonResponse({'redirect': reverse('admin_mfa_settings')})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class AdminMfaSettingsPasskeyRenameView(View):
    def post(self, request, pk):
        passkey = get_object_or_404(PasskeyCredential, pk=pk, user=request.user)
        try:
            payload = json.loads(request.body)
            name = payload.get('name')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid payload.'}, status=400)
        if not name or not str(name).strip():
            return JsonResponse({'detail': 'name is required.'}, status=400)
        passkey.name = str(name).strip()[:255]
        passkey.save(update_fields=['name'])
        return JsonResponse({'id': passkey.pk, 'name': passkey.name})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class AdminMfaSettingsPasskeyDeleteView(View):
    def post(self, request, pk):
        passkey = get_object_or_404(PasskeyCredential, pk=pk, user=request.user)
        allowed, detail = policy.passkey_revoke_allowed(request.user, passkey)
        if not allowed:
            return JsonResponse({'detail': detail}, status=403)
        passkey.delete()
        messages.success(request, 'Passkey removed.')
        return JsonResponse({'ok': True})
