from django.shortcuts import render
from django.template import loader

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')