from rest_framework import serializers
from django.contrib.auth.models import User
from Chat.models import PrivateChat, ChatRoom, ChatRequest, Message


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PrivateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateChat
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.SerializerMethodField()

    def get_sender_username(self, message):
        return message.sender.username if message.sender else None

    class Meta:
        model = Message
        fields = ['id', 'object_id', 'text', 'sender', 'sender_username', 'date_posted']


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['title', 'date_created']
        read_only_fields = ['id', 'owner', 'chat_users']


class ChatRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = '__all__'
