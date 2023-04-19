from rest_framework.test import APITestCase
from users.models import User
from users.serializers import UserSerializer
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class UserSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='John',
            last_name='Doe'
        )
        self.serializer = UserSerializer(instance=self.user)

    def test_create_user_with_no_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='testpassword',
                first_name='John',
                last_name='Doe'
            )

    def test_create_user_with_existing_email_raises_error(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='testpassword',
                first_name='Jane',
                last_name='Doe'
            )

    def test_user_serializer_create(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'newuserpassword',
            'first_name': 'New',
            'last_name': 'User',
        }
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.date_joined)
        self.assertIsNotNone(user.avatar)

    def test_user_serializer_update(self):
        data = {
            'email': 'test@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'is_active': False,
        }
        serializer = UserSerializer(instance=self.user, data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_active)

    def test_email_can_be_changed(self):
        data = {'email': 'newemail@example.com', 'password': 'newpassword'}
        serializer = UserSerializer(
            instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertNotEqual(self.user.email, 'test@example.com')

    def test_serializer_returns_all_fields(self):
        expected_fields = ['id', 'email', 'first_name', 'last_name',
                           'is_active', 'is_staff', 'date_joined', 'avatar']
        data = self.serializer.data
        self.assertCountEqual(data.keys(), expected_fields)

    def test_serializer_does_not_return_password_field(self):
        self.assertNotIn('password', self.serializer.data.keys())

    def test_serializer_returns_correct_avatar_url(self):
        data = self.serializer.data
        self.assertEqual(
            data['avatar'],
            f'/media/avatars/default_avatar.jpg'
        )

    def test_serializer_handles_null_avatar_field(self):
        self.user.avatar = None
        self.user.save()
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertIsNone(data['avatar'])
