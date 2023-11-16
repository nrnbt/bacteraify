from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
import hashlib

def user_login(request):
  try:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        print(form)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=username, password=password)
            if user is not None and not user.is_superuser:
                login(request, user)
                return redirect('home')
            else: 
                messages.error(request, 'Error: Authentication failed!')
                return render(request, 'pages/login.html')
        else :
            messages.error(request, 'Error: Authentication failed!')
            return render(request, 'pages/login.html', { 'form': form })
    else: 
        return render(request, 'pages/login.html')
  except Exception as e:
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/login.html')

def user_logout(request):
  logout(request)
  return redirect('home')

def password_reset_confirm(request, uidb64=None, token=None, email=None):
    def error_callback():
        messages.error(request, 'The password reset link is invalid, possibly because it has already been used. Please request a new password reset.')
        return render(request, 'registration/password_reset_confirm.html')
    
    assert uidb64 is not None and token is not None and email is not None

    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_user_model().objects.get(id=uid)
    if user is not None:
        _token = hashlib.sha256(email.encode() + str(uid).encode()).hexdigest()
        if token == _token:
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your password has been set successfully!')
                    return redirect('login')
                else:
                    messages.error(request, form)
                    return render(request, 'registration/password_reset_confirm.html', { 'form': form })
            else:
                form = SetPasswordForm(user)
                return render(request, 'registration/password_reset_confirm.html', { 'form': form })
        else:
            error_callback()
    else:
        error_callback()