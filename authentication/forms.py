from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserAuth

class UserAuthCreationForm(UserCreationForm):
    class Meta(UserChangeForm.Meta):
        model = UserAuth
        fields = ('email', 'corporateId', 'corporateName')
    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_unusable_password()
    #     if commit:
    #         user.save()
    #     return user

class UserAuthChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserAuth
        fields = ('email', 'corporateId', 'corporateName')