# Generated by Django 5.0.1 on 2024-02-26 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveData', '0005_alter_activity_activity_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_activity_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liveData.activity', unique=True),
        ),
    ]
