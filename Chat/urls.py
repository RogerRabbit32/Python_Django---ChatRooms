from django.urls import path

from .views import index, room, register_user, login_user, logout_user, chat_room_detail, profile


urlpatterns = [
    path("", index, name="index"),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    # path("<str:room_name>/", room, name="room"),
    path('private/<int:chat_id>/', chat_room_detail, name='chat_room_detail'),
    path('profile/', profile, name='profile')
]
