# Generated by Django 5.0.1 on 2024-03-23 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveData', '0008_report_report_audio_report_report_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='report_audio',
        ),
        migrations.RemoveField(
            model_name='report',
            name='report_image',
        ),
        migrations.RemoveField(
            model_name='report',
            name='report_text',
        ),
        migrations.AddField(
            model_name='report',
            name='report_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]