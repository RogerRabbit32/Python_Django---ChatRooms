from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import PrivateChat
from .forms import SignUpForm
from api.serializers import *


@login_required
def chat_room_detail(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    # Check if the current user is a participant in this private chat
    if request.user != chat.user1 and request.user != chat.user2:
        # handle the access denial
        return render(request, 'access_denied.html')

    context = {
        'chat': chat,
    }
    return render(request, 'chat/private_chat_detail.html', context)


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
        return render(request, "chat/register.html", {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('index')
        else:
            messages.success(request, 'There was an error logging in, please try again')
            return redirect('index')
    else:
        return render(request, 'chat/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('index')
