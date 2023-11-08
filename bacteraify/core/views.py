from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def survery(request):
    return render(request, 'survey.html')

def faq(request):
    return render(request, 'faq.html')