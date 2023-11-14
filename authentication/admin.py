from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAuth

class AdminPrivilege(UserAdmin):
    model = UserAuth
    list_display = ['username', 'email', 'corporateId', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('corporateId',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('corporateId',)}),
    )

admin.site.register(UserAuth, AdminPrivilege)
