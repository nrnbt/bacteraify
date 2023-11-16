from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from admin_soft.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout, get_user_model
from django.views import View
from .forms import CustomerCreationForm

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
    return render(request, 'admin-pages/index.html')

def customers(request):
    users = get_user_model().objects.all()
    return render(request, 'admin-pages/customers.html',  {'users': users})

def admin_logout(request):
    logout(request)
    return redirect('admin-login')

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerCreationForm()
        return render(request, 'admin-pages/register-customer.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-customers')
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