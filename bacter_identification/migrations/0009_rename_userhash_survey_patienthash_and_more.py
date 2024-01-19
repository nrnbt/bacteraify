# Generated by Django 4.2.7 on 2024-01-18 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0008_alter_survey_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='survey',
            old_name='userHash',
            new_name='patientHash',
        ),
        migrations.RenameField(
            model_name='survey',
            old_name='type',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='survey',
            old_name='number',
            new_name='surveyNumber',
        ),
        migrations.AddField(
            model_name='survey',
            name='modelTypes',
            field=models.TextField(default='cnn'),
        ),
    ]
