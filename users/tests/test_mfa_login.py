import datetime

import pyotp
from django.test import TestCase, override_settings
from django.utils import timezone
from zoneinfo import ZoneInfo

from app.tests.base_test import BaseTest
from users.models import PasskeyCredential, UserTotpDevice
from users.mfa.tokens import issue_jwt_pair_for_user

ENFORCEMENT_PAST = datetime.datetime(2020, 1, 1, tzinfo=ZoneInfo('America/New_York'))
ENFORCEMENT_FUTURE = datetime.datetime(2099, 1, 1, tzinfo=ZoneInfo('America/New_York'))


class MFALoginTests(BaseTest, TestCase):
    def setUp(self):
        self.clean_tests()

    def test_regular_user_login_without_mfa(self):
        self.user_factory(username='plainuser', password='test1234!')
        response = self.client.post(
            '/api/token/',
            {'username': 'plainuser', 'password': 'test1234!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_staff_without_mfa_gets_enrollment_required(self):
        self.user_factory(username='staffuser', password='test1234!', is_staff=True)
        response = self.client.post(
            '/api/token/',
            {'username': 'staffuser', 'password': 'test1234!'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data.get('mfa_enrollment_required'))
        self.assertIn('enrollment_token', response.data)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_staff_with_totp_requires_second_step(self):
        user = self.user_factory(username='staff2', password='test1234!', is_staff=True)
        secret = pyotp.random_base32()
        UserTotpDevice.objects.create(user=user, secret=secret, confirmed=True)

        response = self.client.post(
            '/api/token/',
            {'username': 'staff2', 'password': 'test1234!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('mfa_required'))
        self.assertIn('totp', response.data.get('methods', []))

        challenge_id = response.data['challenge_id']
        code = pyotp.TOTP(secret).now()
        mfa_response = self.client.post(
            '/api/auth/mfa/totp/verify/',
            {'challenge_id': challenge_id, 'code': code},
            format='json',
        )
        self.assertEqual(mfa_response.status_code, 200)
        self.assertIn('access', mfa_response.data)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_totp_enrollment_via_enrollment_token(self):
        user = self.user_factory(username='staff3', password='test1234!', is_staff=True)
        login_response = self.client.post(
            '/api/token/',
            {'username': 'staff3', 'password': 'test1234!'},
            format='json',
        )
        enrollment_token = login_response.data['enrollment_token']

        setup = self.client.post(
            '/api/auth/mfa/totp/setup/begin/',
            {'enrollment_token': enrollment_token},
            format='json',
        )
        self.assertEqual(setup.status_code, 200)
        secret = setup.data['secret']

        confirm = self.client.post(
            '/api/auth/mfa/totp/setup/confirm/',
            {'enrollment_token': enrollment_token, 'code': pyotp.TOTP(secret).now()},
            format='json',
        )
        self.assertEqual(confirm.status_code, 200)

        login_response = self.client.post(
            '/api/token/',
            {'username': 'staff3', 'password': 'test1234!'},
            format='json',
        )
        self.assertTrue(login_response.data.get('mfa_required'))

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_FUTURE)
    def test_staff_without_mfa_may_login_during_grace_period(self):
        self.user_factory(username='staffgrace', password='test1234!', is_staff=True)
        response = self.client.post(
            '/api/token/',
            {'username': 'staffgrace', 'password': 'test1234!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertTrue(response.data.get('mfa_setup_recommended'))
        self.assertIn('mfa_enforcement_starts_at', response.data)

    def _auth_as(self, user):
        # Users with passkeys must finish MFA at login (WebAuthn can't run here),
        # so issue the post-MFA JWT directly.
        access = issue_jwt_pair_for_user(user)['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_list_rename_and_revoke_passkeys(self):
        user = self.user_factory(username='pkuser', password='test1234!')
        p1 = PasskeyCredential.objects.create(
            user=user, credential_id='cred-1', public_key='pk1', name='Laptop',
        )
        PasskeyCredential.objects.create(
            user=user, credential_id='cred-2', public_key='pk2', name='Phone',
        )
        self._auth_as(user)

        listed = self.client.get('/api/auth/mfa/passkeys/')
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 2)
        self.assertEqual(listed.data[0]['name'], 'Phone')

        renamed = self.client.patch(
            f'/api/auth/mfa/passkeys/{p1.pk}/',
            {'name': 'Work MacBook'},
            format='json',
        )
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.data['name'], 'Work MacBook')
        self.assertIn('created_at', renamed.data)

        deleted = self.client.delete(f'/api/auth/mfa/passkeys/{p1.pk}/')
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(PasskeyCredential.objects.filter(user=user).count(), 1)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_staff_cannot_revoke_last_passkey_without_totp(self):
        # Staff with a single passkey and no TOTP: revoking it would leave no second factor.
        user = self.user_factory(username='staffpk', password='test1234!', is_staff=True)
        pk = PasskeyCredential.objects.create(
            user=user, credential_id='staff-cred-1', public_key='pk', name='Only key',
        )
        self._auth_as(user)

        blocked = self.client.delete(f'/api/auth/mfa/passkeys/{pk.pk}/')
        self.assertEqual(blocked.status_code, 403)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_staff_may_revoke_passkey_when_totp_enabled(self):
        user = self.user_factory(username='staffpk2', password='test1234!', is_staff=True)
        secret = pyotp.random_base32()
        UserTotpDevice.objects.create(user=user, secret=secret, confirmed=True)
        pk = PasskeyCredential.objects.create(
            user=user, credential_id='staff-cred-2', public_key='pk', name='YubiKey',
        )
        pk2 = PasskeyCredential.objects.create(
            user=user, credential_id='staff-cred-3', public_key='pk2', name='Backup',
        )

        login = self.client.post(
            '/api/token/',
            {'username': 'staffpk2', 'password': 'test1234!'},
            format='json',
        )
        tokens = self.client.post(
            '/api/auth/mfa/totp/verify/',
            {'challenge_id': login.data['challenge_id'], 'code': pyotp.TOTP(secret).now()},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens.data["access"]}')

        ok = self.client.delete(f'/api/auth/mfa/passkeys/{pk.pk}/')
        self.assertEqual(ok.status_code, 204)

        ok2 = self.client.delete(f'/api/auth/mfa/passkeys/{pk2.pk}/')
        self.assertEqual(ok2.status_code, 204)

    @override_settings(MFA_STAFF_ENFORCEMENT_START=ENFORCEMENT_PAST)
    def test_staff_may_revoke_one_of_multiple_passkeys_without_totp(self):
        user = self.user_factory(username='staffpk3', password='test1234!', is_staff=True)
        pk1 = PasskeyCredential.objects.create(
            user=user, credential_id='multi-1', public_key='pk', name='A',
        )
        pk2 = PasskeyCredential.objects.create(
            user=user, credential_id='multi-2', public_key='pk2', name='B',
        )

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        ok = self.client.delete(f'/api/auth/mfa/passkeys/{pk1.pk}/')
        self.assertEqual(ok.status_code, 204)

        blocked = self.client.delete(f'/api/auth/mfa/passkeys/{pk2.pk}/')
        self.assertEqual(blocked.status_code, 403)
