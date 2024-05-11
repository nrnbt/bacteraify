from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from authentication.forms import EmailAuthForm
from authentication.models import MerchantEmployee, MerchantAdmin
import hashlib
import logging
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import os
from django.http import HttpResponseBadRequest, HttpResponse
import json

logger = logging.getLogger(__name__)

def merch_home(request):
    if request.user is not None and request.user.is_authenticated and not request.user.is_superuser and request.user.user_type is not None and request.user.user_type == 'MA':
        return render(request, 'pages/merch-admin/index.html')
    else:
        return redirect('merch-login')
    
def merch_dashboard(request):
    if request.user is not None and request.user.is_authenticated and not request.user.is_superuser and request.user.user_type is not None and request.user.user_type == 'MA':
        return render(request, 'pages/merch-admin/dashboard.html')
    else:
        return redirect('merch-login')

def merch_employee(request):
    if request.user is not None and request.user.is_authenticated and not request.user.is_superuser and request.user.user_type is not None and request.user.user_type == 'MA':
        merch_employees = MerchantEmployee.objects.filter(merchant_id=request.user.merchant_id)
        return render(request, 'pages/merch-admin/employee.html', {'merch_employees': merch_employees})
    else:
        return redirect('merch-login')

def employee_register(request):
    if request.user is not None and request.user.is_authenticated and not request.user.is_superuser and request.user.user_type is not None and request.user.user_type == 'MA' and request.method == 'POST':
        try:        
            email = request.POST.get('email')

            merchant_employee = MerchantEmployee(
                email=email,
                merchant_id=request.user.merchant_id,
                created_by=request.user.email
            )
            merchant_employee.save()

            user = MerchantEmployee.objects.get(email=email)

            if user is not None:
                token = hashlib.sha256(email.encode() + str(user.id).encode()).hexdigest()
                uid = urlsafe_base64_encode(force_bytes(user.id))
                type = 'ME'
                password_reset_url = request.build_absolute_uri(
                    reverse('set-password', kwargs={'uidb64': uid, 'token': token, 'email': email, 'type': type})
                )
                send_mail(
                    'Нууц үг тохируулах',
                    f'Follow this link to reset your password: {password_reset_url}',
                    os.environ.get('EMAIL_HOST_USER', 'bacteraify'),
                    [email],
                    fail_silently=False,
                )
                
                return HttpResponse(json.dumps({"sucess": True}), content_type="application/json")
            else:
                messages.error(request, 'Register new employee failed!')
                raise ValueError('Register new employee failed!')
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
    else:
        messages.error(request, "Failed to register new employee.")
        return HttpResponse(None, content_type="application/json")

def merch_emp_login(request):
  try:
    if request.method == 'POST':
        form = EmailAuthForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user.user_type == 'MA':
                raise HttpResponseBadRequest("User type not implemented")
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
        if request.user is not None and request.user.is_authenticated and not request.user.is_superuser:
            return redirect('home')
        else:
            return render(request, 'pages/auth/login.html')

  except Exception as e:
    logger.error(e)
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/auth/login.html')
  
def merch_admin_login(request):
  try:
    if request.method == 'POST':
        form = EmailAuthForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user.user_type == 'ME':
                raise HttpResponseBadRequest("User type not implemented")
            if user is not None and not user.is_superuser:
                login(request, user)
                return redirect('merch-home')
            else:
                messages.error(request, 'Error: Authentication failed!')
                return render(request, 'pages/auth/merch-login.html')
        else :
            logger.error(form.errors)
            messages.error(request, 'Error: Authentication failed!')
            return render(request, 'pages/auth/merch-home.html', { 'form': form })
    else:
        if request.user is not None and request.user.is_authenticated and not request.user.is_superuser:
            return redirect('merch-home')
        else:
            return render(request, 'pages/auth/merch-home.html')

  except Exception as e:
    logger.error(e)
    messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/auth/merch-login.html')

def user_logout(request):
  logout(request)
  return redirect('home')

def reset_pass(request):
  try:
    if request.method == 'POST':
        recipient_email = request.POST['email']

        user = MerchantAdmin.objects.get(email=recipient_email)
        user_type = 'MA'

        if user is not None:
            user = MerchantEmployee.objects.get(email=recipient_email)
            user_type = 'ME'

        if user is not None:
            token = hashlib.sha256(recipient_email.encode() + str(user.id).encode()).hexdigest()
            uid = urlsafe_base64_encode(force_bytes(user.id))
            password_reset_url = request.build_absolute_uri(
                reverse('set-password', kwargs={'uidb64': uid, 'token': token, 'email': recipient_email, 'type': user_type})
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

def password_reset_confirm(request, uidb64=None, token=None, email=None, type=None):
    def error_callback():
        messages.error(request, 'The password reset link is invalid, possibly because it has already been used. Please request a new password reset.')
        return render(request, 'pages/auth/password_reset_confirm.html')
    
    assert uidb64 is not None and token is not None and email is not None and type is not None

    uid = force_str(urlsafe_base64_decode(uidb64))
    user = None

    if type == 'ME':
        user = MerchantEmployee.objects.get(id=uid)
    elif type == 'MA':
        user = MerchantAdmin.objects.get(id=uid)
    else:
        raise ValueError("User type is not implemented")

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
