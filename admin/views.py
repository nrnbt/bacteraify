from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from admin_soft.forms import LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout
from authentication.models import MerchantAdmin
from authentication.forms import MerchantAdminRegisterForm, EmailAuthForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import authenticate, login
from bacter_identification.models import Survey
from django.contrib import messages
import hashlib
import logging
import os
from django.utils import timezone
from admin.statistics import get_all_survey_number, get_all_user_number, new_users_monthly, surveys_monthly, result_by_customer

logger = logging.getLogger(__name__)
current_year = timezone.now().year

def index(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')
    else:
        return redirect('admin-login')

class AdminLoginView(LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin-dashboard')
        else:
            return super().get(request, *args, **kwargs)
        
def admin_login(request):
    try:
        if request.method == 'POST':
            form = EmailAuthForm(request, data=request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = authenticate(email=email, password=password)
                if user is not None and user.is_superuser:
                    login(request, user)
                    return redirect('admin-dashboard')
                else: 
                    messages.error(request, 'Error: Authentication failed!')
                    return render(request, 'account/login.html',  { 'form': form })
            else :
                logger.error(form.errors)
                messages.error(request, 'Error: Authentication failed!')
                return render(request, 'account/login.html', { 'form': form })
        else:
            if  request.user is not None and request.user.is_authenticated:
                return redirect('home')
            else:
                return render(request, 'account/login.html', { 'form': LoginForm() })
    except Exception as e:
        messages.error(request, e)
        logger.error(e)
        return render(request, 'account/login.html', { 'form': LoginForm() })
    
def admin_logout(request):
    logout(request)
    return redirect('admin-login')

def dashboard(request):
    surveys = Survey.objects.all()
    statistics = [
        {
            'name': 'Нийт Merchant',
            'number' : get_all_user_number(),
            'icon': 'ni-world'
        },
        {
            'name': 'Нийт Шинжилгээ',
            'number' : get_all_survey_number(),
            'icon': 'ni-money-coins'
        }
    ]
    monthly_row_count, monthly_survey_count = surveys_monthly()
    context= {
        'statistics_total': statistics,
        'segment': 'Dashboard',
        'surveys': surveys,
        'monthly_row_count': monthly_row_count,
        'monthly_survey_count': monthly_survey_count,
        'monthly_new_users': new_users_monthly(),
    }
    return render(request, 'admin-pages/index.html', context)

def merchants(request):
    users = MerchantAdmin.objects.filter(is_superuser=0)
    context = {
        'users': users,
        'segment': 'Merchants'
    }
    return render(request, 'admin-pages/merchants.html', context)

def register_merchant(request):
    if request.method == 'POST':
        try:
            form = MerchantAdminRegisterForm(request.POST)
            if form.is_valid():
                form.save()

                recipient_email = form.cleaned_data['email']
                users = MerchantAdmin.objects.get(email=recipient_email)

                if users is not None:
                    token = hashlib.sha256(recipient_email.encode() + str(users.id).encode()).hexdigest()
                    uid = urlsafe_base64_encode(force_bytes(users.id))
                    type = 'MA'
                    password_reset_url = request.build_absolute_uri(
                        reverse('set-password', kwargs={'uidb64': uid, 'token': token, 'email': recipient_email, 'type': type})
                    )
                    send_mail(
                        'Нууц үг тохируулах',
                        f'Follow this link to reset your password: {password_reset_url}',
                        os.environ.get('EMAIL_HOST_USER', 'bacteraify'),
                        [recipient_email],
                        fail_silently=False,
                    )
                    return redirect('admin-merchants')
                else:
                    messages.error(request, 'Error: User not registered')
                    return render(request, 'admin-pages/register-merchant-admin.html', {'form': form})
                
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
            return render(request, 'admin-pages/register-merchant-admin.html', {'form': form})
            
    else:
        form = MerchantAdminRegisterForm()
    return render(request, 'admin-pages/register-merchant-admin.html', {'form': form})

class UserPasswordResetView(PasswordResetView):
  template_name = 'account/password_reset.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'account/password_reset_confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'account/password_change.html'
  form_class = UserPasswordChangeForm

def PasswordResetCompleteView(request):
    return render(request, 'account/password_reset_complete.html')

def PasswordResetDoneView(request):
    return render(request, 'account/password_reset_done.html')

def PasswordChangeDoneView(request):
    return render(request, 'account/password_change_done.html')

def merchant(request, id=None):
    if id is not None:
        user = MerchantAdmin.objects.get(id=id)
        surveys = Survey.objects.filter(userId=user.id)

        if user is not None:
            monthly_row_count, monthly_survey_count = surveys_monthly(user.id)
            context= {
                'user': user,
                'segment': 'Merchant',
                'surveys': surveys,
                'monthly_row_count': monthly_row_count,
                'monthly_survey_count': monthly_survey_count,
                'merged_suvrey_result': result_by_customer(user.id),
            }
            return render(request, 'admin-pages/merchant.html', context)
        else:
            messages.error(request, 'Error: Merchant not found')
            return redirect('admin-merchants')
    else:
        messages.error(request, 'Error: id not found')
        return redirect('admin-merchants')