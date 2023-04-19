import uuid

from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Chat(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to='avatars/',
        default='avatars/default_avatar.jpg'
    )
    title = models.TextField()
    is_private = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    admin = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='admin'
    )
    members = models.ManyToManyField(
        User,
        related_name='chats'
    )

    def __str__(self) -> str:
        return f'{self.id}'

    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    text = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    is_read = models.BooleanField(
        default=False
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='messages'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ['-created_at']
