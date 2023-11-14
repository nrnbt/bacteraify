from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model
from django.views import View
from .forms import CustomerCreationForm

def index(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')
    else:
        return redirect('admin-login')

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