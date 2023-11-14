from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def user_login(request):
  try:
    if request.method == 'POST':
        print(request)
        form = AuthenticationForm(request, data=request.POST)
        print(form)
        print(form.errors)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and not user.is_staff:
                login(request, user)
                return redirect('home')
            else: 
                messages.error(request, 'Error: Authentication failed!')
                return render(request, 'pages/login.html')
        else :
            messages.error(request, 'Error: Authentication failed!')
            return render(request, 'pages/login.html')
    else: 
        return render(request, 'pages/login.html')
  except Exception as e:
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/login.html')

def user_logout(request):
  logout(request)
  return redirect('home')
