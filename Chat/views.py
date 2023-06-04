from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import PrivateChat, ChatRoom, ChatRequest
from .forms import SignUpForm, ProfileForm
from api.serializers import *


@login_required
def chat_room_detail(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    # Check if the current user is a participant in this private chat
    if request.user != chat.user1 and request.user != chat.user2:
        # handle the access denial
        return render(request, 'chat/access_denied.html')

    context = {
        'chat': chat,
    }
    return render(request, 'chat/private_chat_detail.html', context)


@login_required
def public_chat_room_detail(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)
    # Check if the current user is a participant in this chat
    if request.user != chat.owner and not chat.chat_users.filter(id=request.user.id).exists():
        # handle the access denial
        return render(request, 'chat/access_denied.html')

    context = {
        'chat': chat,
    }
    return render(request, 'chat/chat_room_detail.html', context)


def index(request):
    chat_rooms = ChatRoom.objects.all()
    user = request.user
    if user.is_authenticated:
        sent_requests = ChatRequest.objects.filter(sender=user)
        sent_requests_chat_ids = [request.chat.id for request in sent_requests]
    else:
        sent_requests_chat_ids = []
    return render(request, "chat/index.html", {
        'public_chats': chat_rooms,
        'sent_request_chat_ids': sent_requests_chat_ids,
    })


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
            return redirect('index')
        else:
            return redirect('index')
    else:
        return render(request, 'chat/login.html')


def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    user = request.user
    approval_requests = ChatRequest.objects.filter(chat__owner=user, is_accepted=False)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Handle the form submission success
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, "chat/profile.html", {'user': user, 'approval_requests': approval_requests, 'form': form})

