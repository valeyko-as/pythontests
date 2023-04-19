from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from chats.models import Chat, Message
from chats.serializers import MessageSerializer

User = get_user_model()


class ChatViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@top.com', password='password1')
        self.user2 = User.objects.create_user(
            email='user2@top.com', password='password2')
        self.client.force_authenticate(user=self.user1)
        self.chat_data = {
            'title': 'Test Chat',
            'members': [self.user2.pk, self.user1.pk],
        }

    def test_create_chat(self):
        url = reverse('chat-list')
        response = self.client.post(url, self.chat_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Chat.objects.first().members.count(), 2)

    def test_create_chat_with_insufficient_members(self):
        url = reverse('chat-list')
        data = {
            'title': 'Test Chat',
            'members': [self.user1.pk],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Chat.objects.count(), 0)

    def test_retrieve_chat(self):
        chat = Chat.objects.create(admin=self.user1, title='Test Chat')
        chat.members.add(self.user1, self.user2)
        url = reverse('chat-detail', kwargs={'pk': chat.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(chat.pk))

    def test_list_chats(self):
        chat1 = Chat(title='chat1')
        chat2 = Chat(title='chat2')
        chat1.members.set([self.user1.pk, self.user2.pk])
        chat2.members.set([self.user1.pk, self.user2.pk])
        chat1.save()
        chat2.save()
        url = reverse('chat-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_chat_unauthenticated(self):
        self.client = APIClient()
        url = reverse('chat-list')
        response = self.client.post(url, self.chat_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Chat.objects.count(), 0)

    def test_retrieve_chat_unauthenticated(self):
        chat = Chat.objects.create(admin=self.user1, title='Test Chat')
        chat.members.add(self.user1, self.user2)
        self.client.logout()
        url = reverse('chat-detail', kwargs={'pk': chat.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_chats_unauthenticated(self):
        chat1 = Chat(title='chat1')
        chat2 = Chat(title='chat2')
        chat1.members.set([self.user1.pk, self.user2.pk])
        chat2.members.set([self.user1.pk, self.user2.pk])
        chat1.save()
        chat2.save()
        self.client.logout()
        url = reverse('chat-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_chat(self):
        chat = Chat(title='Test Chat')
        chat.members.set([self.user1.id])
        chat.save()
        url = reverse('chat-detail', kwargs={'pk': chat.pk})
        data = {
            'title': 'Updated Chat',
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chat.refresh_from_db()
        self.assertEqual(chat.title, 'Updated Chat')

    def test_delete_chat(self):
        chat = Chat.objects.create(admin=self.user1, title='Test Chat')
        chat.members.add(self.user1, self.user2)
        url = reverse('chat-detail', kwargs={'pk': chat.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Chat.objects.count(), 0)


class MessageViewSetTestCase(APITestCase):
    def setUp(self):
        self.chat = Chat.objects.create(title='Test Chat')
        self.message = Message.objects.create(
            text='Test message',
            user=None,
            chat=self.chat
        )
        self.user = User.objects.create_user(
            email='testuser@kek.ru', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_get_all_messages(self):
        url = reverse('message-list')
        response = self.client.get(url)
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_message(self):
        url = reverse('message-detail', args=[str(self.message.id)])
        response = self.client.get(url)
        serializer = MessageSerializer(self.message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_message(self):
        url = reverse('message-list')
        data = {'text': 'New message', 'chat': self.chat.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)

    def test_get_unread_messages(self):
        chat = Chat(title='Unread Chat')
        new_user = User.objects.create(email='kek@kek.ru', password='haha')
        chat.members.set([self.user.id, new_user.id])
        chat.save()
        message = Message.objects.create(
            text='Unread message',
            user=self.user,
            chat=chat
        )
        self.message.save()
        url = reverse('message-get-unread-messages')
        response = self.client.get(url)
        serializer = MessageSerializer([message], many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_message_with_invalid_chat(self):
        url = reverse('message-list')
        data = {'text': 'New message', 'chat': 'invalid_chat_id'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_messages_for_chat(self):
        url = reverse('message-list')
        response = self.client.get(url, {'chat': self.chat.id})
        messages = Message.objects.filter(chat=self.chat)
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_message(self):
        url = reverse('message-detail', args=[str(self.message.id)])
        data = {'text': 'Updated message'}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.get(
            id=self.message.id).text, 'Updated message')

    def test_delete_message(self):
        url = reverse('message-detail', args=[str(self.message.id)])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Message.objects.count(), 0)
