from django.contrib import admin
from django.utils.html import format_html
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'avatar_display',
        'is_active',
        'is_staff'
    ]
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['avatar_display']
    ordering = ['email']

    def avatar_display(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)

    avatar_display.short_description = 'Avatar'


admin.site.register(User, UserAdmin)
