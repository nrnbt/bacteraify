from django.contrib.auth.models import AbstractUser
from django.db import models

class UserAuth(AbstractUser):
    corporateId = models.CharField(max_length=100, blank=True)

# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models

# class AdminPrivilege(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Users must have an email address')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(email, password, **extra_fields)

# class UserAuth(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     # is_active = models.BooleanField(default=True)
#     # is_staff = models.BooleanField(default=False)
#     corporateId = models.CharField(max_length=7, blank=True)
    
#     objects = AdminPrivilege()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.email

