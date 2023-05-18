from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import PrivateChat, ChatRoom
from .serializers import *


class PrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user1_id = request.data.get('user1_id')
        user2_id = request.data.get('user2_id')

        # Check if a private chat already exists between the two users
        existing_private_chat = PrivateChat.objects.filter(
            (Q(user1=user1_id) & Q(user2=user2_id)) |
            (Q(user1=user2_id) & Q(user2=user1_id))
        ).first()

        if existing_private_chat:
            serializer = PrivateChatSerializer(existing_private_chat)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            new_chat = PrivateChat.objects.create(user1=user1_id, user2=user2_id)
            serializer = PrivateChatSerializer(new_chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@login_required
def chat_room_detail(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    # Check if the current user is a participant in this private chat
    if request.user != chat.user1 and request.user != chat.user2:
        # handle the access denial
        return render(request, 'access_denied.html')

    # Retrieve the last 15 messages in the chat
    messages = Message.objects.filter(
        content_type=ContentType.objects.get_for_model(chat),
        object_id=chat.id,
    ).order_by('date_posted')[:15]

    context = {
        'chat': chat,
        'messages': messages,
    }
    return render(request, 'chat/private_chat_detail.html', context)


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
