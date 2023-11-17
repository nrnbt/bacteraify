# Generated by Django 4.2.7 on 2023-11-17 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_userauth_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.IntegerField()),
                ('userEmail', models.EmailField(max_length=254)),
                ('fileName', models.CharField(max_length=255)),
                ('rowNumber', models.IntegerField()),
                ('type', models.CharField(max_length=50)),
            ],
        ),
    ]
