import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model
from chats.models import Chat, Message

User = get_user_model()


class ChatModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@test.ru',
            password='testpass'
        )
        self.chat = Chat.objects.create(
            title='Test Chat',
            admin=self.user
        )

    def test_chat_creation(self):
        self.assertIsInstance(self.chat, Chat)
        self.assertEqual(str(self.chat), str(self.chat.id))
        self.assertEqual(self.chat.title, 'Test Chat')
        self.assertEqual(self.chat.admin, self.user)

    def test_chat_add_member(self):
        new_user = User.objects.create(
            email='test2@test.ru',
            password='testpass'
        )
        self.chat.members.add(new_user)
        self.assertIn(new_user, self.chat.members.all())

    def test_chat_remove_member(self):
        new_user = User.objects.create(
            email='test2@test.ru',
            password='testpass'
        )
        self.chat.members.add(new_user)
        self.chat.members.remove(new_user)
        self.assertNotIn(new_user, self.chat.members.all())

    def test_chat_has_default_avatar(self):
        self.assertEqual(self.chat.avatar.name, 'avatars/default_avatar.jpg')

    def test_chat_is_private_by_default(self):
        self.assertTrue(self.chat.is_private)

    def test_chat_str_method(self):
        expected_output = str(self.chat.id)
        self.assertEqual(str(self.chat), expected_output)

    def test_chat_members(self):
        new_user = User.objects.create(
            email='test2@test.ru',
            password='testpass'
        )
        self.chat.members.add(new_user)
        self.assertEqual(self.chat.members.count(), 1)

    def test_chat_admin_can_be_null(self):
        chat = Chat.objects.create(
            title='Test Chat 2'
        )
        self.assertIsNone(chat.admin)

    def test_chat_with_duplicate_members(self):
        new_user = User.objects.create(
            email='test2@test.ru',
            password='testpass'
        )
        self.chat.members.add(new_user)
        self.chat.members.add(new_user)
        self.assertEqual(self.chat.members.count(), 1)
        self.assertEqual(self.chat.members.first().id, new_user.id)

    def test_chat_remove_non_member(self):
        non_member = User.objects.create(
            email='test3@test.ru',
            password='testpass'
        )
        self.chat.members.remove(non_member)
        self.assertNotIn(non_member, self.chat.members.all())


class MessageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@test.ru',
            password='testpass'
        )
        self.chat = Chat.objects.create(
            title='Test Chat',
            admin=self.user
        )
        self.message = Message.objects.create(
            text='Test message',
            user=self.user,
            chat=self.chat
        )

    def test_message_creation(self):
        self.assertIsInstance(self.message, Message)
        self.assertEqual(str(self.message.id), str(self.message.id))
        self.assertEqual(self.message.text, 'Test message')
        self.assertEqual(self.message.user, self.user)
        self.assertEqual(self.message.chat, self.chat)

    def test_message_read(self):
        self.assertFalse(self.message.is_read)
        self.message.is_read = True
        self.assertTrue(self.message.is_read)

    def test_message_is_not_read_by_default(self):
        self.assertFalse(self.message.is_read)

    def test_message_has_created_at_field(self):
        self.assertIsNotNone(self.message.created_at)

    def test_message_str_method(self):
        self.assertEqual(str(self.message), self.message.text)

    def test_message_chat_cascade_delete(self):
        self.chat.delete()
        self.assertFalse(Message.objects.filter(id=self.message.id).exists())
