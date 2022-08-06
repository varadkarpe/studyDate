from bdb import GENERATOR_AND_COROUTINE_FLAGS
from ctypes import sizeof
from itertools import count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from .models import Message, Room, Topic
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User

# Create your views here.
from django.http import HttpResponse

""" rooms = [
    {'id': 0, 'name': 'This room does not exist'},
    {'id':1, 'name': 'Common room'},
    {'id': 2, 'name': 'Meeting Room 1'},
    {'id': 3, 'name': 'Meeting Room 2'},
] """

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password incorrect")
    context = {'page' : page}
    return render(request, 'base/login_register.html', context)

def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
        else: 
            messages.error(request, 'Registration unsuccessful')
    return render(request, 'base/login_register.html', {'form' : form})

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) | Q(name__icontains = q) | Q(description__icontains = q)) if q != '' else Room.objects.all()
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id = pk)
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room, 
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room' : room, 'usermessages' : room.message_set.all().order_by('-created'), 'participants' : room.participants.all()}
    return render(request, 'base/room.html', context)

@login_required(login_url = '/login')
def createRoom(request):
    form = RoomForm({'host' : request.user})
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url= '/login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)
    if request.user != room.host:
        return HttpResponse('Request not valid')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance = room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = '/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse('Request not valid')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})

@login_required(login_url = '/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)
    if request.user != message.user:
        return HttpResponse('Not your comment to delete')
    if request.method == 'POST':
        message.delete()
        return redirect('room', pk = message.room.id)
    return render(request, 'base/delete.html', {'obj' : message})