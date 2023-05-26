from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import PrivateChat, ChatRoom
from .forms import SignUpForm
from .serializers import *


class PrivateChatView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve both the private chat users from the database
        user1_id, user2_id = request.data.get('user1_id'), request.data.get('user2_id')
        first_user, second_user = User.objects.get(id=user1_id), User.objects.get(id=user2_id)

        # Check if a private chat already exists between the two users
        existing_private_chat = PrivateChat.objects.filter(
            (Q(user1=first_user) & Q(user2=second_user)) |
            (Q(user1=second_user) & Q(user2=first_user))
        ).first()

        # If so, return the chat data, otherwise - create the chat between them
        if existing_private_chat:
            serializer = PrivateChatSerializer(existing_private_chat)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            new_chat = PrivateChat.objects.create(user1=first_user, user2=second_user)
            serializer = PrivateChatSerializer(new_chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, chat_id):
        chat = get_object_or_404(PrivateChat, id=chat_id)

        if request.user != chat.user1 and request.user != chat.user2:
            # handle the access denial
            return render(request, 'access_denied.html')

        messages = Message.objects.filter(
            content_type=ContentType.objects.get_for_model(chat),
            object_id=chat.id,
        ).order_by('date_posted')[:15]
        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)


class MessageAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(PrivateChat, id=chat_id)

        if request.user != chat.user1 and request.user != chat.user2:
            # handle the access denial
            return Response({'error': 'Access denied'}, status=403)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Create the message
            message = serializer.save(content_object=chat, sender=request.user)
            # Serialize the created message
            serialized_message = MessageSerializer(message)

            return Response(serialized_message.data, status=201)

        return Response(serializer.errors, status=400)

    def get(self, request):
        # Get all private chats created by the current requesting user
        private_chats = PrivateChat.objects.filter(user1=request.user) | PrivateChat.objects.filter(user2=request.user)

        # Get all messages associated with the private chats
        messages = Message.objects.filter(content_type__model='privatechat', object_id__in=private_chats.values('id'))

        # Serialize the messages
        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)


@login_required
def chat_room_detail(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    # Check if the current user is a participant in this private chat
    if request.user != chat.user1 and request.user != chat.user2:
        # handle the access denial
        return render(request, 'access_denied.html')

    context = {
        'chat': chat,
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


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
        return render(request, "chat/register.html", {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('index')
        else:
            messages.success(request, 'There was an error logging in, please try again')
            return redirect('index')
    else:
        return render(request, 'chat/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('index')
