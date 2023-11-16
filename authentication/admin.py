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

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import UserAuth

# class Admin(UserAdmin):
#     model = UserAuth
#     list_display = ['email', 'password', 'corporateId']
#     list_filter = ['email', 'password', 'corporateId']
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Permissions', {'fields': ('is_active')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'is_active')}
#         ),
#     )
#     search_fields = ('email',)
#     ordering = ('email',)

# admin.site.register(UserAuth, Admin)