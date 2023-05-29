from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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
        # Check user permissions
        if request.user != chat.user1 and request.user != chat.user2:
            # Handle the access denial
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


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

