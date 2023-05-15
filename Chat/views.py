from django.shortcuts import render
from rest_framework import generics
from .models import ChatRoom
from .serializers import ChatRoomSerializer
from django.contrib.auth.models import User
from .serializers import *


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