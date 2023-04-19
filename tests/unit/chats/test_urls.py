from django.test import SimpleTestCase
from django.urls import reverse, resolve
from chats.views import ChatViewSet, MessageViewSet


class TestUrls(SimpleTestCase):

    def test_chat_list_url(self):
        url = reverse('chat-list')
        self.assertEquals(resolve(url).func.cls, ChatViewSet)

    def test_chat_detail_url(self):
        url = reverse('chat-detail', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.cls, ChatViewSet)

    def test_chat_detail_url(self):
        url = reverse('chat-add-members', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.cls, ChatViewSet)

    def test_message_list_url(self):
        url = reverse('message-list')
        self.assertEquals(resolve(url).func.cls, MessageViewSet)

    def test_message_detail_url(self):
        url = reverse('message-detail')
        self.assertEquals(resolve(url).func.cls, MessageViewSet)

    def test_message_detail_url(self):
        url = reverse('message-get-unread-messages')
        self.assertEquals(resolve(url).func.cls, MessageViewSet)
