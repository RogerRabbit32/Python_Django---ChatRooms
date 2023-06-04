from django.urls import path

from .views import index, register_user, login_user, logout_user, chat_room_detail, profile, public_chat_room_detail


urlpatterns = [
    path("", index, name="index"),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('private/<int:chat_id>/', chat_room_detail, name='chat_room_detail'),
    path('profile/', profile, name='profile'),
    path('room/<int:chat_id>/', public_chat_room_detail, name='public_chat_room_detail'),
]

