from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PrivateChat(models.Model):
    user1 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user1')
    user2 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user2')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Between {self.user1.username} and {self.user2.username}'


class ChatRoom(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    chat_users = models.ManyToManyField(User, related_name='chat_users')
    date_created = models.DateTimeField(auto_now_add=True)

    def add_participant(self, user):
        self.chat_users.add(user)

    def __str__(self):
        return f'{self.title} by {self.owner}'


class Message(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date_posted = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
