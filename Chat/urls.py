from django.urls import path

from .views import index, room, UserList


urlpatterns = [
    path("", index, name="index"),
    path("<str:room_name>/", room, name="room"),
    path('api/users/', UserList.as_view(), name='user-list'),
]
