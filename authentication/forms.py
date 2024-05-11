from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MerchantAdmin
from django.contrib.auth.forms import AuthenticationForm

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

class EmailAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)

    email = forms.EmailField(label="Email", max_length=254)
