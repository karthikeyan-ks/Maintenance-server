# Generated by Django 5.0.1 on 2024-04-01 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveData', '0012_users_logged'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='token',
            field=models.CharField(default='token', max_length=255),
        ),
    ]
