from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserAuth
from django.contrib.auth import authenticate

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    corporateId = forms.CharField(label='Corporate ID', max_length=7, required=True)
    corporateName = forms.CharField(label='Corporate Name', max_length=100, required=True)
    class Meta(forms.ModelForm):
        model = UserAuth
        fields = ('email', 'corporateId', 'corporateName')

class UserAuthCreationForm(UserCreationForm):
    class Meta(UserChangeForm.Meta):
        model = UserAuth
        fields = ('email', 'corporateId', 'corporateName')

class UserAuthChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserAuth
        fields = ('email', 'corporateId', 'corporateName')