from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PrivateChat, ChatRoom, Message


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
        fields = ['id', 'text', 'sender', 'sender_username', 'date_posted']


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
