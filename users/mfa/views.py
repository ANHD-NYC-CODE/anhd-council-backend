from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from users import models as u
from users.mfa import challenge as mfa_challenge
from users.mfa import passkey_service
from users.mfa import policy
from users.mfa import totp_service
from users.mfa.tokens import issue_jwt_pair_for_user


def _maybe_update_last_login(user):
    if jwt_api_settings.UPDATE_LAST_LOGIN:
        update_last_login(None, user)


def _staff_mfa_grace_payload(user):
    if not policy.staff_in_mfa_grace_period(user):
        return {}
    deadline = policy.mfa_staff_grace_deadline()
    return {
        'mfa_setup_recommended': True,
        'mfa_enforcement_starts_at': deadline.isoformat() if deadline else None,
    }


class MFATokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is None or not jwt_api_settings.USER_AUTHENTICATION_RULE(user):
            return Response(
                {'detail': 'No active account found with the given credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        step = policy.login_step_after_password(user)
        if step == 'complete':
            _maybe_update_last_login(user)
            payload = issue_jwt_pair_for_user(user)
            payload.update(_staff_mfa_grace_payload(user))
            return Response(payload)

        if step == 'enrollment_required':
            enrollment_token = mfa_challenge.create_enrollment_session(user.pk)
            deadline = policy.mfa_staff_grace_deadline()
            detail = (
                'Admin accounts must register at least one second factor '
                '(authenticator app or passkey) before signing in.'
            )
            if deadline:
                detail = (
                    f'{detail} Required since {deadline.strftime("%B %-d, %Y")} '
                    f'({deadline.tzname()}).'
                )
            return Response(
                {
                    'mfa_enrollment_required': True,
                    'enrollment_token': enrollment_token,
                    'mfa_enforcement_starts_at': deadline.isoformat() if deadline else None,
                    'detail': detail,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        challenge_id = mfa_challenge.create_mfa_challenge(user.pk)
        return Response(
            {
                'mfa_required': True,
                'challenge_id': challenge_id,
                'methods': policy.available_mfa_methods(user),
            },
            status=status.HTTP_200_OK,
        )


class MFATotpVerifyView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        challenge_id = request.data.get('challenge_id')
        code = request.data.get('code')
        if not challenge_id or not code:
            return Response({'detail': 'challenge_id and code are required.'}, status=400)

        session = mfa_challenge.get_mfa_challenge(challenge_id)
        if not session or session.get('kind') != 'mfa':
            return Response({'detail': 'Invalid or expired challenge.'}, status=400)

        user = u.CustomUser.objects.filter(pk=session['user_id']).first()
        if not user or not totp_service.verify_totp_code(user, code):
            return Response({'detail': 'Invalid verification code.'}, status=401)

        mfa_challenge.consume_mfa_challenge(challenge_id)
        _maybe_update_last_login(user)
        return Response(issue_jwt_pair_for_user(user))


class MFATotpSetupBeginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        user = _resolve_user_for_setup(request)
        if not user:
            return Response({'detail': 'Unauthorized.'}, status=401)

        device = totp_service.get_or_create_pending_totp(user)
        if device is None:
            return Response({'detail': 'TOTP is already enabled.'}, status=400)

        return Response(
            {
                'secret': device.secret,
                'otpauth_url': totp_service.provisioning_uri(device),
            }
        )


class MFATotpSetupConfirmView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        user = _resolve_user_for_setup(request)
        if not user:
            return Response({'detail': 'Unauthorized.'}, status=401)

        code = request.data.get('code')
        if not code:
            return Response({'detail': 'code is required.'}, status=400)

        if not totp_service.confirm_totp_device(user, code):
            return Response({'detail': 'Invalid verification code.'}, status=400)

        if policy.user_requires_mfa_enrollment(user):
            return Response({'detail': 'TOTP enabled. You may also add a passkey.'})

        return Response({'detail': 'TOTP enabled.'})


class MFAPasskeyRegisterBeginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        user = _resolve_user_for_setup(request)
        if not user:
            return Response({'detail': 'Unauthorized.'}, status=401)

        scope_key = _webauthn_scope_key(request, user.pk)
        try:
            options = passkey_service.begin_registration(user, scope_key)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'publicKey': options})


class MFAPasskeyRegisterCompleteView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        user = _resolve_user_for_setup(request)
        if not user:
            return Response({'detail': 'Unauthorized.'}, status=401)

        credential = request.data.get('credential')
        name = request.data.get('name') or 'Passkey'
        if not credential:
            return Response({'detail': 'credential is required.'}, status=400)

        scope_key = _webauthn_scope_key(request, user.pk)
        try:
            passkey_service.complete_registration(user, scope_key, credential, name=name)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)

        if policy.user_requires_mfa_enrollment(user):
            return Response(
                {
                    'detail': 'Passkey registered.',
                    'mfa_enrollment_required': True,
                },
                status=200,
            )
        return Response({'detail': 'Passkey registered.'})


class MFAPasskeyAuthenticateBeginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        challenge_id = request.data.get('challenge_id')
        if not challenge_id:
            return Response({'detail': 'challenge_id is required.'}, status=400)

        session = mfa_challenge.get_mfa_challenge(challenge_id)
        if not session or session.get('kind') != 'mfa':
            return Response({'detail': 'Invalid or expired challenge.'}, status=400)

        user = u.CustomUser.objects.filter(pk=session['user_id']).first()
        if not user:
            return Response({'detail': 'Invalid challenge.'}, status=400)

        try:
            options = passkey_service.begin_authentication(user, challenge_id)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'publicKey': options})


class MFAPasskeyAuthenticateCompleteView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        challenge_id = request.data.get('challenge_id')
        credential = request.data.get('credential')
        if not challenge_id or not credential:
            return Response({'detail': 'challenge_id and credential are required.'}, status=400)

        session = mfa_challenge.get_mfa_challenge(challenge_id)
        if not session or session.get('kind') != 'mfa':
            return Response({'detail': 'Invalid or expired challenge.'}, status=400)

        user = u.CustomUser.objects.filter(pk=session['user_id']).first()
        if not user:
            return Response({'detail': 'Invalid challenge.'}, status=400)

        try:
            passkey_service.complete_authentication(user, challenge_id, credential)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=401)

        mfa_challenge.consume_mfa_challenge(challenge_id)
        _maybe_update_last_login(user)
        return Response(issue_jwt_pair_for_user(user))


def _serialize_passkey(passkey):
    return {
        'id': passkey.pk,
        'name': passkey.name,
        'created_at': passkey.created_at.isoformat(),
    }


class MFAPasskeyListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        passkeys = u.PasskeyCredential.objects.filter(user=request.user).order_by('-created_at')
        return Response([_serialize_passkey(p) for p in passkeys])


class MFAPasskeyDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def _get_owned_passkey(self, user, pk):
        return u.PasskeyCredential.objects.filter(user=user, pk=pk).first()

    def patch(self, request, pk):
        passkey = self._get_owned_passkey(request.user, pk)
        if not passkey:
            return Response({'detail': 'Passkey not found.'}, status=404)

        name = request.data.get('name')
        if name is None or not str(name).strip():
            return Response({'detail': 'name is required.'}, status=400)

        passkey.name = str(name).strip()[:255]
        passkey.save(update_fields=['name'])
        return Response(_serialize_passkey(passkey))

    def delete(self, request, pk):
        passkey = self._get_owned_passkey(request.user, pk)
        if not passkey:
            return Response({'detail': 'Passkey not found.'}, status=404)

        allowed, detail = policy.passkey_revoke_allowed(request.user, passkey)
        if not allowed:
            return Response({'detail': detail}, status=403)

        passkey.delete()
        return Response(status=204)


class MFAStatusView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        user = request.user
        deadline = policy.mfa_staff_grace_deadline()
        return Response(
            {
                'mfa_required_for_role': user.is_mfa_required_role(),
                'mfa_enforcement_active': policy.mfa_enforcement_active(),
                'mfa_enforcement_starts_at': deadline.isoformat() if deadline else None,
                'mfa_setup_recommended': policy.staff_in_mfa_grace_period(user),
                'totp_enabled': policy.user_has_confirmed_totp(user),
                'passkey_count': u.PasskeyCredential.objects.filter(user=user).count(),
                'methods': policy.available_mfa_methods(user),
            }
        )


def _resolve_user_for_setup(request):
    enrollment_token = request.data.get('enrollment_token')
    if enrollment_token:
        session = mfa_challenge.get_enrollment_session(enrollment_token)
        if not session:
            return None
        return u.CustomUser.objects.filter(pk=session['user_id']).first()

    if request.user and request.user.is_authenticated:
        return request.user
    return None


def _webauthn_scope_key(request, user_id):
    enrollment_token = request.data.get('enrollment_token')
    if enrollment_token:
        return f'enroll:{enrollment_token}'
    return f'user:{user_id}'
