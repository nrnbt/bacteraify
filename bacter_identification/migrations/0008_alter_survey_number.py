# Generated by Django 4.2.7 on 2023-11-24 07:52

import bacter_identification.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0007_survey_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='number',
            field=models.CharField(max_length=10, unique=True, validators=[bacter_identification.models.validate_alpha_numeric]),
        ),
    ]
