from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def user_login(request):
  try:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
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

def password_reset_confirm(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been set successfully!')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, 'The password reset link is invalid, possibly because it has already been used. Please request a new password reset.')
        return redirect('password_reset_confirm')

    return render(request, 'registration/password_reset_confirm.html', {'form': form})
