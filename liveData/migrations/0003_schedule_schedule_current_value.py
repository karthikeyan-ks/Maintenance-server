# Generated by Django 5.0.1 on 2024-02-25 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveData', '0002_demo'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='schedule_current_value',
            field=models.IntegerField(default=0),
        ),
    ]
