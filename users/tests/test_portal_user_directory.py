from django.test import TestCase
from django.urls import reverse

from app.tests.base_test import BaseTest


class PortalUserDirectoryAdminTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_portal_login_increments_login_count(self):
        user = self.user_factory(
            email='portal@test.com',
            username='portaluser',
            password='test1234',
        )
        response = self.client.post(
            '/api/token/',
            {'username': 'portaluser', 'password': 'test1234'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        user.refresh_from_db()
        self.assertEqual(user.login_count, 1)
        self.assertEqual(user.login_days, 1)
        self.assertIsNotNone(user.last_login)

    def test_second_sign_in_same_day_increments_count_not_days(self):
        user = self.user_factory(
            email='twice@test.com',
            username='twiceuser',
            password='test1234',
        )
        for _ in range(2):
            response = self.client.post(
                '/api/token/',
                {'username': 'twiceuser', 'password': 'test1234'},
                format='json',
            )
            self.assertEqual(response.status_code, 200, response.data)
        user.refresh_from_db()
        self.assertEqual(user.login_count, 2)
        self.assertEqual(user.login_days, 1)

    def test_staff_user_excluded_from_portal_directory(self):
        staff = self.user_factory(
            email='staff@test.com',
            username='staffuser',
            password='test1234',
            is_staff=True,
        )
        portal = self.user_factory(
            email='member@test.com',
            username='memberuser',
            password='test1234',
        )
        admin_user = self.user_factory(
            email='admin@test.com',
            username='adminuser',
            password='test1234',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)
        url = reverse('admin:users_portaluserdirectory_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(portal.email, content)
        self.assertNotIn(staff.email, content)

    def test_admin_index_shows_portal_user_shortcuts(self):
        admin_user = self.user_factory(
            email='indexadmin@test.com',
            username='indexadmin',
            password='test1234',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Download portal users CSV', content)
        self.assertIn(reverse('admin:users_portaluserdirectory_export_csv'), content)

    def test_staff_without_superuser_can_view_directory(self):
        staff = self.user_factory(
            email='staffonly@test.com',
            username='staffonly',
            password='test1234',
            is_staff=True,
            is_superuser=False,
        )
        self.client.force_login(staff)
        url = reverse('admin:users_portaluserdirectory_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_export_csv_requires_staff(self):
        url = reverse('admin:users_portaluserdirectory_export_csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_export_csv_without_double_question_mark(self):
        admin_user = self.user_factory(
            email='csvadmin@test.com',
            username='csvadmin',
            password='test1234',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)
        url = reverse('admin:users_portaluserdirectory_export_csv')
        self.assertEqual(self.client.get(url).status_code, 200)
        # Broken template produced export-csv/?? which Django parsed as field "?".
        self.assertEqual(self.client.get(url + '?').status_code, 200)

    def test_export_csv_returns_rows(self):
        portal = self.user_factory(
            email='export@test.com',
            username='exportuser',
            password='test1234',
        )
        admin_user = self.user_factory(
            email='admin2@test.com',
            username='admin2',
            password='test1234',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)
        url = reverse('admin:users_portaluserdirectory_export_csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        body = response.content.decode()
        header = body.splitlines()[0]
        self.assertIn('email', header)
        self.assertIn('sign_ins_total', header)
        self.assertIn('login_days', header)
        self.assertIn('login_metrics_since', header)
        self.assertIn(portal.email, body)
