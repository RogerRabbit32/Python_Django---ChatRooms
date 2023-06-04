from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/private_chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/public_chat/(?P<public_chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]