from django.test import TestCase
from django.contrib.auth import get_user_model
from chats.models import Chat, Message
from chats.serializers import ChatSerializer, MessageSerializer

User = get_user_model()


class ChatSerializerTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(
            email='test1@test.ru',
            password='testpass1'
        )
        self.user2 = User.objects.create(
            email='test2@test.ru',
            password='testpass2'
        )

    def test_chat_serializer_valid_data(self):
        data = {
            'title': 'Test Chat',
            'members': [self.user1.id, self.user2.id],
            'is_private': True
        }
        serializer = ChatSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        chat = serializer.save(admin=self.user1)
        self.assertIsInstance(chat, Chat)
        self.assertEqual(chat.title, 'Test Chat')
        self.assertIn(self.user1, chat.members.all())
        self.assertIn(self.user2, chat.members.all())
        self.assertTrue(chat.is_private)

    def test_chat_serializer_missing_title(self):
        data = {
            'members': [self.user1.id, self.user2.id],
            'is_private': True
        }
        serializer = ChatSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['title']))

    def test_chat_serializer_missing_members(self):
        data = {
            'title': 'Test Chat',
            'is_private': True
        }
        serializer = ChatSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['members']))

    def test_chat_serializer_invalid_members(self):
        data = {
            'title': 'Test Chat',
            'members': [self.user1.id],
            'is_private': True
        }
        serializer = ChatSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['members']))
        self.assertIn('Chat should have at least two members',
                      serializer.errors['members'][0])


class MessageSerializerTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='test1@test.ru',
            password='testpass1'
        )
        self.user2 = User.objects.create_user(
            email='test2@test.ru',
            password='testpass2'
        )
        self.chat = Chat.objects.create(
            title='Test Chat',
            admin=self.user1
        )

    def test_message_serializer_valid_data(self):
        data = {
            'text': 'Test message',
            'user': self.user1.id,
            'chat': self.chat.id
        }
        serializer = MessageSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        message = serializer.save()
        self.assertIsInstance(message, Message)
        self.assertEqual(message.text, 'Test message')
        self.assertEqual(message.user, self.user1)
        self.assertEqual(message.chat, self.chat)

    def test_message_serializer_missing_text(self):
        data = {
            'user': self.user1.id,
            'chat': self.chat.id
        }
        serializer = MessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['text']))

    def test_message_serializer_missing_chat_id(self):
        data = {
            'text': 'Test message',
            'user': self.user1.id
        }
        serializer = MessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['chat']))

    def test_message_serializer_missing_chat(self):
        data = {
            'text': 'Test message',
            'user': self.user1.id
        }
        serializer = MessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['chat']))

    def test_message_serializer_invalid_user_id(self):
        data = {
            'text': 'Test message',
            'user': 9999,
            'chat': self.chat.id
        }
        serializer = MessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['user']))

    def test_message_serializer_invalid_chat_id(self):
        data = {
            'text': 'Test message',
            'user': self.user1.id,
            'chat': 9999
        }
        serializer = MessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['chat']))
