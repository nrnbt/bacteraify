# Generated by Django 4.2.7 on 2023-11-22 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='userHash',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
