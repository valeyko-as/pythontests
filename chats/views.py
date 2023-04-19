from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Message, Chat
from .serializers import MessageSerializer, ChatSerializer
from users.serializers import UserSerializer, User


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['GET'], detail=False, url_path='unread')
    def get_unread_messages(self, request):
        messages = Message.objects.filter(
            chat__members=request.user, is_read=False)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        return super().get_permissions()

    @action(methods=['PATCH'], detail=True)
    def add_members(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        members = request.data.get('members')
        if not isinstance(members, (list, tuple)):
            members = [members]
        for member_id in members:
            member = get_object_or_404(User, id=member_id)
            chat.members.add(member)
        return Response({'flag': 'ok'}, status=status.HTTP_201_CREATED)
