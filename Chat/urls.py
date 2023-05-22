from django.urls import path

from .views import index, room, UserList, chat_room_detail, PrivateChatView, MessageAPIView


urlpatterns = [
    path("", index, name="index"),
    path("<str:room_name>/", room, name="room"),
    path('api/users/', UserList.as_view(), name='user-list'),
    path('private/<int:chat_id>/', chat_room_detail, name='chat_room_detail'),
    path('api/private_chats/', PrivateChatView.as_view(), name='private-chats'),
    path('api/private_chats/<int:chat_id>/', PrivateChatView.as_view(), name='private_chat_history'),
    path('api/messages/', MessageAPIView.as_view(), name='all-messages'),
    path('api/messages/<int:chat_id>/', MessageAPIView.as_view(), name='chat-messages'),
]
