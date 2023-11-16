from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from admin_soft.forms import LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout, get_user_model
from django.views import View
from authentication.forms import UserAuthCreationForm
from django.contrib.auth.tokens import default_token_generator
import os 
from django.core.mail import send_mail

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
    # def form_valid(self, form):
    #     return redirect('admin-dashboard')


# def login(request):
#     if request.method == 'Post':
#         return render(request, 'admin-pages/login.html')
#     else:
#         return render(request, 'admin-pages/login.html')
    
# def pass_reset(request):
#     if request.method == 'Post':
#         return render(request, 'admin-pages/pass_reset.html')
#     else:
#         return render(request, 'admin-pages/pass_reset.html')

def dashboard(request):
    return render(request, 'admin-pages/index.html', { 'segment': 'Dashboard' })

def customers(request):
    users = get_user_model().objects.all()
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
        form = UserAuthCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # send_mail(
            #      'Set Your Password',
            #     f'Please set your password using this token: {token}',
            #     'from@example.com',
            #     [user.email],
            #     fail_silently=False,
            # )
                # request = HttpRequest()
                # request.META['SERVER_NAME'] = os.environ.get('SERVER_NAME', 'bacteraify.com')
                # request.META['SERVER_PORT'] = os.environ.get('SERVER_PORT', '8000')
                # reset_form.save(
                #     request=request,
                #     use_https=True,
                #     email_template_name='registration/password_reset_email.html',
                #     subject_template_name='registration/password_reset_subject.txt'
                # )

            return redirect('success_url')
    else:
        form = UserAuthCreationForm()
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