from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from Chat.models import PrivateChat, ChatRoom, ChatRequest
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


class ChatRequestCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            chat = serializer.validated_data['chat']
            user = serializer.validated_data['sender']
            # Check if the chat owner is sending the request to join
            if chat.owner == user:
                return Response({'detail': 'You are the owner of this chat.'},
                                status=status.HTTP_400_BAD_REQUEST)
            # Check if the user has already sent a request for the chat
            if ChatRequest.objects.filter(chat=chat, sender=user).exists():
                return Response({'detail': 'You have already sent a request to join this chat.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRequestApprovalView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        try:
            chat_request = ChatRequest.objects.get(id=request_id)
        except ChatRequest.DoesNotExist:
            return Response({'detail': 'A chat participation request with this id does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        if request.user != chat_request.chat.owner:
            return Response({'detail': 'You can only approve requests to your own chats'},
                            status=status.HTTP_400_BAD_REQUEST)
        chat_request.approve_request()
        return Response(status=status.HTTP_200_OK)


class ChatRoomView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, chat_id):
        chat = get_object_or_404(ChatRoom, id=chat_id)
        # Check if the current user is a participant in this chat
        if request.user != chat.owner and not chat.chat_users.filter(id=request.user.id).exists():
            # handle the access denial
            return render(request, 'access_denied.html')

        messages = Message.objects.filter(
            content_type=ContentType.objects.get_for_model(chat),
            object_id=chat.id,
        ).order_by('date_posted')[:15]
        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)

    def patch(self, request, chat_id):
        chat = get_object_or_404(ChatRoom, id=chat_id)
        # Check if the current user is the owner of the chat room
        if request.user != chat.owner:
            return Response({'detail': 'You are not the owner of this chat room.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ChatRoomSerializer(chat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
