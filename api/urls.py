from django.urls import path

from .views import UserList, PrivateChatView, MessageAPIView


urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('private_chats/', PrivateChatView.as_view(), name='private-chats'),
    path('private_chats/<int:chat_id>/', PrivateChatView.as_view(), name='private_chat_history'),
    path('messages/', MessageAPIView.as_view(), name='all-messages'),
    path('messages/<int:chat_id>/', MessageAPIView.as_view(), name='chat-messages'),
]
