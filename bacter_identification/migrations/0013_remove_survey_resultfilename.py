# Generated by Django 4.2.7 on 2024-01-18 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0012_alter_survey_cnnpredfilename_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='resultFileName',
        ),
    ]