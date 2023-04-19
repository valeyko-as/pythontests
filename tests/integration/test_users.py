from rest_framework.reverse import reverse
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


class UserViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='John',
            last_name='Doe'
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)
        self.url = reverse('user-list')

    def test_create_user_success(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_missing_email(self):
        data = {
            'password': 'newpassword',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_email(self):
        data = {
            'email': 'test@example.com',
            'password': 'newpassword',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_by_email(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('user-search'), {'query': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['email'], self.user.email)

    def test_update_user(self):
        data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName'
        }
        url = reverse('user-detail', args=[self.user.id])
        response = self.auth_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.last_name, data['last_name'])

    def test_partial_update_user(self):
        data = {
            'first_name': 'UpdatedFirstName',
        }
        url = reverse('user-detail', args=[self.user.id])
        response = self.auth_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.last_name, 'Doe')

    def test_delete_user(self):
        url = reverse('user-detail', args=[self.user.id])
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())

    def test_search_users(self):
        User.objects.create_user(
            email='anotheruser@example.com',
            password='anotherpassword',
            first_name='Alice',
            last_name='Smith'
        )
        query = '@example.com'
        response = self.auth_client.get(
            reverse('user-search'), {'query': query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['email'], self.user.email)

    def test_search_users_no_query(self):
        response = self.auth_client.get(reverse('user-search'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_active_users(self):
        User.objects.create_user(
            email='inactiveuser@example.com',
            password='inactivepassword',
            first_name='Inactive',
            last_name='User',
            is_active=False
        )
        response = self.auth_client.get(reverse('user-active-users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], self.user.email)

    def test_permissions_create_user(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permissions_retrieve_user(self):
        url = reverse('user-detail', args=[self.user.id])
        self.auth_client.logout()
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_update_another_user(self):
        user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpassword2',
            first_name='Jane',
            last_name='Doe'
        )
        data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName'
        }
        url = reverse('user-detail', args=[user2.id])
        response = self.auth_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
