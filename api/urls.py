from django.urls import path

from .views import UserList, PrivateChatView, MessageAPIView, ChatRequestCreateView, ChatRequestApprovalView, \
ChatRoomView


urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('private_chats/', PrivateChatView.as_view(), name='private-chats'),
    path('private_chats/<int:chat_id>/', PrivateChatView.as_view(), name='private_chat_history'),
    path('messages/', MessageAPIView.as_view(), name='all-messages'),
    path('messages/<int:chat_id>/', MessageAPIView.as_view(), name='chat-messages'),
    path('chat_rooms/requests/create/', ChatRequestCreateView.as_view(), name='chat-request'),
    path('chat_rooms/requests/<int:request_id>/approve/', ChatRequestApprovalView.as_view(), name='request-approval'),
    path('chat_rooms/create/', ChatRoomView.as_view(), name='chat-room-create'),
    path('chat_rooms/<int:chat_id>/', ChatRoomView.as_view(), name='chat_room_history'),
    # path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]
