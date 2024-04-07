import asyncio
import json
from datetime import datetime

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .firebase import sendBroadCast

from .models import Activity, Task, Status, Users, Report


@receiver(post_save, sender=Activity)
def on_database_change(sender, instance, created, **kwargs):
    print("triggered")
    sendBroadCast("admin", {
        'name': instance.activity_name,
        'description': instance.activity_description,
        'creator': instance.activity_creator.user_name,
        'change': "created" if created else "updated",
        'model': "activity",
        'broadcast': str(True)
    })
    task = Task.objects.filter(task_activity_id=instance.activity_id).first()
    channels_layer = channels.layers.get_channel_layer()
    if not created:
        if instance.activity_status_id == Status.objects.filter(status_id=1).first():
            print("task already exist so deleting it" + instance.activity_name)
            if task is not None:
                task.delete()
            print("sending ...")
            body = {
                "activity_id": instance.activity_id,
                "activity_descrption": instance.activity_description,
                "actvity_status_id": instance.activity_status_id.status_id,
                "activity_component_id": instance.activity_component_id.component_id,
                "activity_machine_id": instance.activity_machine_id.machine_id,
                "activity_schedule_id": instance.activity_schedule_id.schedule_id,
                "activity_name": instance.activity_name,
                "activity_issued_date": instance.activity_issued_date.strftime("%Y-%m-%d"),
                "activity_last_reported": instance.activity_last_reported.strftime("%Y-%m-%d"),
                "activity_creator": instance.activity_creator.user_name,
                "schedule_value": instance.activity_schedule_value,
                "assigned_to_id": 0,
                "assigned_to_user": "None",
                "change": "create",
                "ui_change": "create"
            }
            async_to_sync(channels_layer.group_send)(
                "admin", {
                    "type": 'send_database_client',
                    "message": body
                }
            )
        elif instance.activity_status_id == Status.objects.filter(status_id=2).first():
            print("task already not exist cant delete" + instance.activity_name)
        elif instance.activity_status_id == Status.objects.filter(status_id=3).first():
            body = {
                "activity_id": instance.activity_id,
                "activity_descrption": instance.activity_description,
                "actvity_status_id": instance.activity_status_id.status_id,
                "activity_component_id": instance.activity_component_id.component_id,
                "activity_machine_id": instance.activity_machine_id.machine_id,
                "activity_schedule_id": instance.activity_schedule_id.schedule_id,
                "activity_name": instance.activity_name,
                "activity_issued_date": instance.activity_issued_date.strftime("%Y-%m-%d"),
                "activity_last_reported": instance.activity_last_reported.strftime("%Y-%m-%d"),
                "activity_creator": instance.activity_creator.user_name,
                "schedule_value": instance.activity_schedule_value,
                "assigned_to_id": task.task_assign_to.user_id,
                "assigned_to_user": task.task_assign_to.user_name,
                "change": "create",
                "ui_change": "update"
            }
            async_to_sync(channels_layer.group_send)(
                "admin", {
                    "type": 'send_database_client',
                    "message": body
                }
            )


@receiver(post_save, sender=Task)
def task_save_change(sender, instance, created, **kwargs):
    channels_layer = channels.layers.get_channel_layer()
    body = {
        "activity_id": instance.task_activity_id.activity_id,
        "activity_descrption": instance.task_activity_id.activity_description,
        "actvity_status_id": instance.task_activity_id.activity_status_id.status_id,
        "activity_component_id": instance.task_activity_id.activity_component_id.component_id,
        "activity_machine_id": instance.task_activity_id.activity_machine_id.machine_id,
        "activity_schedule_id": instance.task_activity_id.activity_schedule_id.schedule_id,
        "activity_name": instance.task_activity_id.activity_name,
        "activity_issued_date": instance.task_activity_id.activity_issued_date.strftime("%Y-%m-%d"),
        "activity_creator": instance.task_activity_id.activity_creator.user_name,
        "assigned_to_id": instance.task_assign_to.user_id,
        "activity_last_reported": instance.task_activity_id.activity_last_reported.strftime("%Y-%m-%d"),
        "schedule_value": instance.task_activity_id.activity_schedule_value,
        "assigned_to_user": instance.task_assign_to.user_name,
        "change": "create" if created else "updated",
        "ui_change": "create" if instance.task_activity_id.activity_status_id == Status.objects.filter(
            status_id=1).first() else "update"
    }
    if created:
        print("created")
    else:
        print("updated")
    async_to_sync(channels_layer.group_send)(
        "admin", {
            "type": 'send_database_client',
            "message": body
        }
    )


@receiver(post_save, sender=Report)
def reportTrigger(sender, instance, **kwargs):
    print("report triggered")
    activity_id = instance.report_activity
    print(activity_id)
    activity_id.activity_last_report = datetime.now()
    activity_id.activity_status_id = Status.objects.filter(status_id=1).first()
    activity_id.save()


@receiver(pre_delete, sender=Activity)
def my_model_pre_delete(sender, instance, **kwargs):
    print("delete trigger")
    body = {
        "activity_id": instance.activity_id,
        "activity_descrption": instance.activity_description,
        "actvity_status_id": instance.activity_status_id.status_id,
        "activity_component_id": instance.activity_component_id.component_id,
        "activity_machine_id": instance.activity_machine_id.machine_id,
        "activity_schedule_id": instance.activity_schedule_id.schedule_id,
        "activity_name": instance.activity_name,
        "activity_issued_date": instance.activity_issued_date.strftime("%Y-%m-%d"),
        "activity_creator": instance.activity_creator.user_name,
        "schedule_value": instance.activity_schedule_value,
        "assigned_to_id": 0,
        "assigned_to_user": "None",
        "change": "delete",
        "ui_change": "create"
    }
    sendBroadCast("admin", {
        'name': instance.activity_name,
        'description': instance.activity_description,
        'creator': instance.activity_creator.user_name,
        'change': "delete",
        'model': "activity"
    })
    activity = instance.activity_id
    if instance.activity_status_id != Status.objects.filter(status_id=2):
        task = Task.objects.filter(task_activity_id=activity).first()
        if task is not None:
            task.delete()
            print("Activity " + str(instance.activity_status_id) + " deleted with associated task " + str(task.task_id))
    else:
        print("Activity was inert")
    pass
