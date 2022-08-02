from bdb import GENERATOR_AND_COROUTINE_FLAGS
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Message, Room
from .forms import RoomForm

# Create your views here.
from django.http import HttpResponse

rooms = [
    {'id': 0, 'name': 'This room does not exist'},
    {'id':1, 'name': 'Common room'},
    {'id': 2, 'name': 'Meeting Room 1'},
    {'id': 3, 'name': 'Meeting Room 2'},
]

def home(request):
    rooms = Room.objects.all()
    context = {'rooms' : rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    context = {'rooms' : Room.objects.get(id = pk) if len(Room.objects.filter(id = pk)) > 0 else "Room does not exist", 'messages' : list(Message.objects.all())}
    return render(request, 'base/room.html', context)

def createRoom(request):
    form = RoomForm
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance = room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)