from rest_framework.reverse import reverse
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_registration(self):
        response = self.client.post(self.register_url, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('access' in response.data)

    def test_login(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('access' in response.data)

    def test_logout(self):
        self.client.login(
            email=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Logged out successfully.')

    def test_obtain_jwt_token_valid_credentials(self):
        User.objects.create_user(**self.user_data)

        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }

        response = self.client.post(reverse('obtain'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_obtain_jwt_token_invalid_credentials(self):
        data = {
            'email': 'wrongemail',
            'password': 'wrongpassword'
        }

        response = self.client.post(reverse('obtain'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Invalid credentials'})

    def test_registration_invalid_email_format(self):
        self.user_data['email'] = 'invalid_email_format'
        response = self.client.post(self.register_url, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_required_fields(self):
        self.user_data.pop('email')
        response = self.client.post(self.register_url, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_email(self):
        login_data = {
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        login_data = {
            'email': self.user_data['email'],
        }
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email(self):
        login_data = {
            'email': 'invalid_email',
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_password(self):
        login_data = {
            'email': self.user_data['email'],
            'password': 'invalid_password',
        }
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
