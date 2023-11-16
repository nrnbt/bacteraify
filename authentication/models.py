from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django import forms
from django.contrib.auth import authenticate, get_user_model

class AdminPrivilege(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserAuth(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, blank=True, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    corporateId = models.CharField(max_length=7, blank=True)
    corporateName = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = AdminPrivilege()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'corporateId']

    def __str__(self):
        return self.email