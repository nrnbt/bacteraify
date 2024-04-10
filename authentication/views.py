from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from authentication.forms import EmailLoginForm
import hashlib
import logging
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import os

logger = logging.getLogger(__name__)

def user_login(request):
  try:
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and not user.is_superuser:
                login(request, user)
                return redirect('home')
            else: 
                messages.error(request, 'Error: Authentication failed!')
                return render(request, 'pages/auth/login.html')
        else :
            logger.error(form.errors)
            messages.error(request, 'Error: Authentication failed!')
            return render(request, 'pages/auth/login.html', { 'form': form })
    else:
        if request.user.is_authenticated and not user.is_superuser:
            return redirect('home')
        else:
            return render(request, 'pages/auth/login.html')

  except Exception as e:
    logger.error(e)
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/auth/login.html')

def user_logout(request):
  logout(request)
  return redirect('home')

def reset_pass(request):
  try:
    if request.method == 'POST':
        recipient_email = request.POST['email']
        users = get_user_model().objects.get(email=recipient_email)

        if users is not None:
            token = hashlib.sha256(recipient_email.encode() + str(users.id).encode()).hexdigest()
            uid = urlsafe_base64_encode(force_bytes(users.id))
            password_reset_url = request.build_absolute_uri(
                reverse('set-password', kwargs={'uidb64': uid, 'token': token, 'email': recipient_email})
            )
            send_mail(
                'Нууц үг тохируулах',
                f'Follow this link to reset your password: {password_reset_url}',
                os.environ.get('EMAIL_HOST_USER', 'bacteraify'),
                [recipient_email],
                fail_silently=False,
            )
            return render(request, 'pages/auth/reset-pass.html', { 'emailSent': True, 'email': recipient_email })
        else:
            messages.error(request, 'Error: Something went wrong!')
            return render(request, 'pages/auth/reset-pass.html')
    else:
        return render(request, 'pages/auth/reset-pass.html')

  except Exception as e:
    logger.error(e)
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/auth/reset-pass.html')

def password_reset_confirm(request, uidb64=None, token=None, email=None):
    def error_callback():
        messages.error(request, 'The password reset link is invalid, possibly because it has already been used. Please request a new password reset.')
        return render(request, 'pages/auth/password_reset_confirm.html')
    
    assert uidb64 is not None and token is not None and email is not None

    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_user_model().objects.get(id=uid)
    if user is not None:
        _token = hashlib.sha256(email.encode() + str(uid).encode()).hexdigest()
        if token == _token:
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    user.is_active = True
                    user.save()  
                    messages.success(request, 'Таны нууц үгийг амжилттай тохирууллаа!')
                    return redirect('login')
                else:
                    # messages.error(request, form) 
                    return render(request, 'pages/auth/password_reset_confirm.html', { 'form': form })
            else:
                form = SetPasswordForm(user)
                return render(request, 'pages/auth/password_reset_confirm.html', { 'form': form })
        else:
            error_callback()
    else:
        error_callback()