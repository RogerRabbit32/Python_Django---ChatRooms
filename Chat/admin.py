from django.contrib import admin
from .models import PrivateChat, ChatRoom, Message

admin.site.register(PrivateChat)
admin.site.register(ChatRoom)
admin.site.register(Message)
