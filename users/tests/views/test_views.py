from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from users import views as v
import logging
logging.disable(logging.CRITICAL)


class UserViews(BaseTest, TestCase):

    def tearDown(self):
        self.clean_tests()

    def test_unauthenticated_get_current_user(self):
        username = 'test'
        password = 'test1234'
        user = self.user_factory(email="test@test.com",  username=username, password=password)

        response = self.client.get('/users/current/', format="json")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_get_current_user(self):
        username = 'test'
        password = 'test1234'
        council = self.council_factory(id=3)
        user = self.user_factory(email="test@test.com",  username=username, password=password)
        profile = self.userprofile_factory(user=user, council=council)
        token = self.get_access_token(username=username, password=password)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get('/users/current/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['username'], 'test')
        self.assertEqual(content['email'], 'test@test.com')
        self.assertEqual(content['profile']['council'], 3)
