from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import RegistrationView, LoginView, LogoutView, obtain_jwt_token


class TestUrls(SimpleTestCase):

    def test_registration_url(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func.cls, RegistrationView)

    def test_login_url(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func.cls, LoginView)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func.cls, LogoutView)

    def test_token_obtain_url(self):
        url = reverse('obtain')
        self.assertEquals(resolve(url).func, obtain_jwt_token)
