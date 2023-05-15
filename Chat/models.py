from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    chat_users = models.ManyToManyField(User, related_name='chat_users')
    date_created = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
