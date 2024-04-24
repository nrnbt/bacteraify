from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MerchantAdmin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

class MerchantAdminRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    merchant_id = forms.CharField(label='Merchant ID', max_length=7, required=True)
    merchant_name = forms.CharField(label='Merchant Name', max_length=100, required=True)
    class Meta(forms.ModelForm):
        model = MerchantAdmin
        fields = ('email', 'merchant_id', 'merchant_name')

class MerchantAdminCreationForm(UserCreationForm):
    class Meta(UserChangeForm.Meta):
        model = MerchantAdmin
        fields = ('email', 'merchant_id', 'merchant_name')

class MerchantAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = MerchantAdmin
        fields = ('email', 'merchant_id', 'merchant_name')

User = get_user_model()

class EmailAuthForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(email=username)
        except User.DoesNotExist:
            raise forms.ValidationError("This email does not exist.")
        return username

class EmailLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')