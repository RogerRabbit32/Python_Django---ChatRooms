from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework import generics

from .models import PrivateChat, ChatRoom
from .serializers import *


@login_required
def chat_room_detail(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    # Check if the current user is a participant in this private chat
    if not chat.filter(user1=request.user.id).exists() and not chat.filter(user2=request.user.id).exists():
        # handle the access denial
        return render(request, 'access_denied.html')

    # Retrieve the last 15 messages in the chat
    messages = Message.objects.filter(
        content_type=ContentType.objects.get_for_model(chat),
        object_id=chat.id,
    ).order_by('-date_created')[:15]

    context = {
        'chat': chat,
        'messages': messages,
    }
    return render(request, 'chat_room_detail.html', context)


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
