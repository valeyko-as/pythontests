from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from chats.models import Message, Chat
from chats.serializers import MessageSerializer, ChatSerializer

User = get_user_model()


class SequentialActionsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com', password='testpass')
        self.user1 = User.objects.create_user(
            email='testuser1@example.com', password='testpass1')
        self.chat = Chat.objects.create()
        self.chat.members.add(self.user)
        self.message = Message.objects.create(
            chat=self.chat, user=self.user, text='Test message')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_tokens()['access'])

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_sequential_actions_1(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Open all messages
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = Message.objects.filter(chat__members=self.user)
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)

        # Read one message
        message = messages[0]
        message.is_read = True
        message.save()
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = MessageSerializer(messages, many=True)
        data = serializer.data
        data[0]['is_read'] = True
        self.assertEqual(response.data, data)

        # Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION='')

        # Ensure user is logged out
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sequential_actions_2(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create a new chat
        response = self.client.post(
            reverse('chat-list'), {'title': 'chatik', 'members': [self.user.id, self.user1.id]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Send a message to the new chat
        chat_id = response.data['id']
        response = self.client.post(
            reverse('message-list'), {'chat': chat_id, 'text': 'New message'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sequential_actions_3(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create a new user
        response = self.client.post(
            reverse('user-list'), {
                'email': 'newuser@example.com',
                'password': 'newpass',
                'first_name': 'kek',
                'last_name': 'kek'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # change chat users
        chat_id = self.chat.id
        user_id = response.data['id']
        response = self.client.patch(
            reverse('chat-detail', args=[chat_id]), {'members': [self.user.id, user_id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sequential_actions_4(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Open chat details
        response = self.client.get(reverse('chat-detail', args=[self.chat.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ChatSerializer(self.chat)
        data = serializer.data
        data.pop('avatar')
        response.data.pop('avatar')
        self.assertEqual(response.data, data)

        # Add new member to chat
        new_user = User.objects.create_user(
            email='testuser2@example.com', password='testpass2')
        response = self.client.patch(
            reverse('chat-add-members', args=[self.chat.id]), {'members': [new_user.id]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sequential_actions_unauthorized_user_5(self):
        self.client = APIClient()

        # Open all messages (should fail)
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Register new user
        response = self.client.post(
            reverse('register'), {'email': 'testuser2@example.com', 'password': 'testpass', 'first_name': 'kek', 'last_name': 'kek'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Login with wrong password
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Login with correct password
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Open all messages (should succeed)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sequential_actions_6(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Open all chats
        response = self.client.get(reverse('chat-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create a new chat
        response = self.client.post(
            reverse('chat-list'), {'members': [self.user.id, self.user1.id], 'title': 'kek'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chat = Chat.objects.get(pk=response.data['id'])
        self.assertEqual(chat.members.count(), 2)

        # Send a message in the new chat
        response = self.client.post(
            reverse('message-list'), {'chat': chat.id, 'text': 'New message'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message = Message.objects.get(pk=response.data['id'])
        self.assertEqual(message.chat, chat)
        self.assertEqual(message.text, 'New message')

        # Logout
        self.client.credentials()
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_user_profile_7(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # View user profile
        response = self.client.get(
            reverse('user-detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')

        # Update user profile
        response = self.client.patch(reverse(
            'user-detail', kwargs={'pk': self.user.pk}), {'email': 'newemail@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')

        # Logout
        self.client.credentials()
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sequential_actions_8(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create a new chat with no members (should fail)
        response = self.client.post(reverse('chat-list'), {'title': 'chatik'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sequential_actions_9(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete a message
        response = self.client.delete(reverse('message-detail', args=[self.message.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the message was deleted
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=self.message.id)

    def test_sequential_actions_10(self):
        # Login
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the chat list
        response = self.client.get(reverse('chat-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the user's chat is in the list
        serializer = ChatSerializer(self.chat)
        data = serializer.data
        data.pop('avatar')
        response.data[0].pop('avatar')
        res_data = response.data[0]
        self.assertEqual(res_data, data)

    def test_sequential_actions_11(self):
        # Register a new user
        response = self.client.post(
            reverse('register'), {'email': 'newuser@example.com', 'password': 'testpass', 'first_name': 'John', 'last_name': 'Doe'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt to register the same user again (should fail)
        response = self.client.post(
            reverse('register'), {'email': 'newuser@example.com', 'password': 'testpass', 'first_name': 'Jane', 'last_name': 'Doe'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sequential_actions_12(self):
        # Login with incorrect email (should fail)
        response = self.client.post(
            reverse('login'), {'email': 'invalid@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Login with incorrect password (should fail)
        response = self.client.post(
            reverse('login'), {'email': 'testuser@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sequential_actions_13(self):
        # Attempt to add a member to a chat without providing a user ID (should fail)
        response = self.client.patch(
            reverse('chat-add-members', args=[self.chat.id]), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Attempt to create a chat without providing a title (should fail)
        response = self.client.post(
            reverse('chat-list'), {'members': [self.user.id]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
