from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from django.db.utils import IntegrityError


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='John',
            last_name='Doe'
        )

    def test_create_user(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertIsNotNone(self.user.date_joined)
        self.assertIsNotNone(self.user.avatar)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password('adminpassword'))
        self.assertEqual(superuser.first_name, 'Admin')
        self.assertEqual(superuser.last_name, 'User')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertIsNotNone(superuser.date_joined)
        self.assertIsNotNone(superuser.avatar)

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'test@example.com')

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'John Doe')

    def test_get_full_name(self):
        self.assertEqual(self.user.get_short_name(), 'John D.')

    def test_avatar_upload(self):
        avatar = SimpleUploadedFile("avatar.jpg", b"file_content")
        self.user.save()
        self.assertIsNotNone(self.user.avatar)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='testpassword',
                first_name='Jane',
                last_name='Doe'
            )

    def test_email_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')

    def test_date_joined(self):
        user = User.objects.create_user(
            email='another@example.com',
            password='testpassword',
            first_name='Jane',
            last_name='Doe'
        )
        self.assertIsNotNone(user.date_joined)

    def test_get_full_name_empty_names(self):
        self.user.first_name = ''
        self.user.last_name = ''
        self.assertEqual(self.user.get_full_name(), '')

    def test_get_short_name_empty_names(self):
        self.user.first_name = ''
        self.user.last_name = ''
        self.assertEqual(self.user.get_short_name(), '1234')

    def test_get_full_name_special_characters(self):
        self.user.first_name = 'J#hn'
        self.user.last_name = 'Doe'
        self.assertEqual(self.user.get_full_name(), 'J#hn Doe')

    def test_get_short_name_special_characters(self):
        self.user.first_name = 'J#hn'
        self.user.last_name = 'Doe'
        self.assertEqual(self.user.get_short_name(), 'J#hn D.')

    def test_create_user_no_email(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(password='testpassword')

    def test_create_user_empty_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpassword')

    def test_create_superuser_no_email(self):
        with self.assertRaises(TypeError):
            User.objects.create_superuser(password='adminpassword')

    def test_create_superuser_empty_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='', password='adminpassword')
