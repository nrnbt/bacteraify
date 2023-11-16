from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from admin_soft.forms import LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout, get_user_model
from django.views import View
from authentication.forms import UserRegisterForm
from django.contrib.auth.tokens import default_token_generator
import os
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
import hashlib

def index(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')
    else:
        return redirect('admin-login')
    
def billing(request):
    return render(request, 'admin-pages/billing.html', { 'segment': 'billing' })

def tables(request):
    return render(request, 'admin-pages/tables.html', { 'segment': 'tables' })

def profile(request):
    return render(request, 'admin-pages/profile.html', { 'segment': 'profile' })

class AdminLoginView(LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin-dashboard')
        else:
            return super().get(request, *args, **kwargs)

def dashboard(request):
    return render(request, 'admin-pages/index.html', { 'segment': 'Dashboard' })

def customers(request):
    users = get_user_model().objects.filter(is_superuser=0)
    context = {
        'users': users,
        'segment': 'Customers'
    }
    return render(request, 'admin-pages/customers.html', context)

def admin_logout(request):
    logout(request)
    return redirect('admin-login')

def register_customer(request):
    if request.method == 'POST':
        try:
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()

                recipient_email = form.cleaned_data['email']
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
                    return redirect('admin-customers')
                else: 
                    messages.error(request, 'Error: User not registered')
                    return render(request, 'admin-pages/register-customer.html', {'form': form})
                
        except Exception as e:
            messages.error(request, e)
            return render(request, 'admin-pages/register-customer.html', {'form': form})
            
    else:
        form = UserRegisterForm()
    return render(request, 'admin-pages/register-customer.html', {'form': form})

class UserPasswordResetView(PasswordResetView):
  template_name = 'account/password_reset.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'account/password_reset_confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'account/password_change.html'
  form_class = UserPasswordChangeForm

def customer(request, id=None):
    if id is not None:
        user = get_user_model().objects.get(id=id)
        if user is not None:
            print(user)
            context= {
                'user': user,
                'segment': 'Customer'
            }
            return render(request, 'admin-pages/customer.html', context)
        else:
            messages.error(request, 'Error: Customer not found')
            return redirect('admin-customers')
    else:
        messages.error(request, 'Error: id not found')
        return redirect('admin-customers')

    