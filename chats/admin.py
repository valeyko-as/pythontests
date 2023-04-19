from django.contrib import admin
from django.utils.html import format_html

from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'admin', 'members_list',
                    'created_at', 'is_private', 'avatar_tag')
    list_filter = ('is_private', 'created_at')
    search_fields = ('id', 'title', 'admin__username', 'members__username')

    def avatar_tag(self, obj):
        return format_html('<img src="{}" width="50" height="50"/>'.format(obj.avatar.url))
    avatar_tag.short_description = 'Avatar'

    def members_list(self, obj):
        members = obj.members.all()
        return ', '.join([member.username for member in members])
    members_list.short_description = 'Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'user', 'chat', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('id', 'text', 'user__username', 'chat__title')
