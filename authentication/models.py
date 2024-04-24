from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    USER_TYPE_CHOICES = (
        ('SA', 'System Admin'),
        ('DA', 'Django Admin'),
        ('MA', 'Merchant Admin'),
        ('ME', 'Merchant Employee'),
    )

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

class SystemAdmin(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=2, choices=UserManager.USER_TYPE_CHOICES, default='SA')
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        permissions = (
            ('system_admin_user_permissions', 'System Admin User Permissions'),
            ('system_admin_permissions', 'System Admin Permissions'),
        )
        db_table = 'system_admin'

    def __str__(self):
        return self.email
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='system_admin_user_permissions'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='system_admin_groups'
    )

class MerchantAdmin(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    merchant_id = models.CharField(max_length=7, blank=True)
    merchant_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=2, choices=UserManager.USER_TYPE_CHOICES, default='MA')

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'merchant_id', 'merchant_name']

    class Meta:
        permissions = (
            ('merchant_admin_user_permissions', 'Merchant Admin User Permissions'),
            ('merchant_admin_permissions', 'Merchant Admin Permissions'),
        )
        db_table = 'merchant_admin'

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='merchant_admin_user_permissions'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='merchant_admin_groups'
    )

class MerchantEmployee(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    merchant_id = models.CharField(max_length=7, blank=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    uploaded_surveys = models.JSONField(default=dict)
    user_type = models.CharField(max_length=2, choices=UserManager.USER_TYPE_CHOICES, default='ME')

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'created_by']

    class Meta:
        permissions = (
            ('merchant_employee_user_permissions', 'Merchant Employee User Permissions'),
            ('merchant_employee_permissions', 'Merchant Employee Permissions'),
        )
        db_table = 'merchant_employee'

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='merchant_employee_user_permissions'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='merchant_employee_groups'
    )
