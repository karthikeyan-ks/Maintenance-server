# Generated by Django 5.0.1 on 2024-02-24 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveData', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Demo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('demo_id', models.CharField(max_length=30)),
            ],
        ),
    ]
