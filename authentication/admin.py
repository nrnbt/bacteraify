from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAuth
from .forms import UserAuthChangeForm, UserAuthCreationForm

class Admin(UserAdmin):
    model = UserAuth
    add_form = UserAuthCreationForm
    form = UserAuthChangeForm
    list_display = ['username','email', 'password', 'corporateId', 'corporateName']
    list_filter = ['username', 'email', 'corporateId', 'corporateName']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email', 'username')