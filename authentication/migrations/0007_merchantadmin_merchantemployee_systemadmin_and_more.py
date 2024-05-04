# Generated by Django 5.0.3 on 2024-04-24 06:30

import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('authentication', '0006_alter_userauth_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='MerchantAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('merchant_id', models.CharField(blank=True, max_length=7)),
                ('merchant_name', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, related_name='merchant_admin_groups', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='merchant_admin_user_permissions', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'merchant_admin',
                'permissions': (('merchant_admin_user_permissions', 'Merchant Admin User Permissions'), ('merchant_admin_permissions', 'Merchant Admin Permissions')),
            },
        ),
        migrations.CreateModel(
            name='MerchantEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('merchant_id', models.CharField(blank=True, max_length=7)),
                ('created_by', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('uploaded_surveys', models.JSONField(default=dict)),
                ('groups', models.ManyToManyField(blank=True, related_name='merchant_employee_groups', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='merchant_employee_user_permissions', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'merchant_employee',
                'permissions': (('merchant_employee_user_permissions', 'Merchant Employee User Permissions'), ('merchant_employee_permissions', 'Merchant Employee Permissions')),
            },
        ),
        migrations.CreateModel(
            name='SystemAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user_type', models.CharField(choices=[('SA', 'System Admin'), ('DA', 'Django Admin'), ('MA', 'Merchant Admin'), ('ME', 'Merchant Employee')], default='SA', max_length=2)),
                ('groups', models.ManyToManyField(blank=True, related_name='system_admin_groups', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='system_admin_user_permissions', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'system_admin',
                'permissions': (('system_admin_user_permissions', 'System Admin User Permissions'), ('system_admin_permissions', 'System Admin Permissions')),
            },
        )
    ]