# Generated by Django 4.2.7 on 2024-01-18 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0009_rename_userhash_survey_patienthash_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='cnnPredFileName',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='survey',
            name='rnnPredFileName',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='survey',
            name='svgPredFileName',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='survey',
            name='modelTypes',
            field=models.TextField(default='CNN'),
        ),
    ]