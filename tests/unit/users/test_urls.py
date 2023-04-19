from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import UserViewSet


class TestUrls(SimpleTestCase):

    def test_user_list_url(self):
        url = reverse('user-list')
        self.assertEquals(resolve(url).func.cls, UserViewSet)

    def test_user_current_url(self):
        url = reverse('user-current-user')
        self.assertEquals(resolve(url).func.cls, UserViewSet)

    def test_user_search_url(self):
        url = reverse('user-search')
        self.assertEquals(resolve(url).func.cls, UserViewSet)

    def test_user_active_url(self):
        url = reverse('user-active-users')
        self.assertEquals(resolve(url).func.cls, UserViewSet)
