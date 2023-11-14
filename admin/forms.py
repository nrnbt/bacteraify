from django import forms
from django.contrib.auth.forms import UserCreationForm
from authentication.models import UserAuth

class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserAuth
        fields = UserCreationForm.Meta.fields + ('corporateId',)
