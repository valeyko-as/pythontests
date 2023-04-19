from rest_framework import serializers

from .models import Message, Chat


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'is_read')


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'admin')

    def validate_members(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                'Chat should have at least two members')
        return value
