# Generated by Django 4.2.7 on 2023-11-17 03:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
