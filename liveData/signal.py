import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Activity, Task, Status


@receiver(post_save, sender=Activity)
def on_database_change(sender, instance, created, **kwargs):
    print("triggered")
    channels_layer = channels.layers.get_channel_layer()
    task = Task.objects.filter(task_activity_id=instance.activity_id).first()
    if task is not None:
        task_assigned_to = task.task_assign_to.user_id
        task_assigned_to_user_name = task.task_assign_to.user_name
    else:
        task_assigned_to = 0
        task_assigned_to_user_name = "None"
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
        "assigned_to": task_assigned_to,
        "assigned_to_user": task_assigned_to_user_name,
        "change": "create" if created else "updated"
    }
    async_to_sync(channels_layer.group_send)(
        "chat_users", {
            "type": 'send_database_client',
            "message": json.dumps(body)
        }
    )
    if created:
        print("created")
    else:
        print("updated")
    """
       
    """
    pass


@receiver(pre_delete, sender=Task)
def my_model_pre_delete(sender, instance, **kwargs):
    activity = instance.task_activity_id
    if activity is not None:
        activity = Activity.objects.filter(activity_id=activity.activity_id).first()
        activity.activity_status_id = Status.objects.filter(status_id=1).first()
        activity.save()
        print(activity.activity_status_id, activity.activity_id)
    else:
        print("activity is already deleted or something.. couldn't found it")
    pass


@receiver(pre_delete, sender=Activity)
def my_model_pre_delete(sender, instance, **kwargs):
    activity = instance.task_activity_id
    if activity.activity_status_id != Status.objects.filter(status_id=2):
        task = Task.objects.filter(task_activity_id=activity).first()
        task.delete()
        print("Activity " + instance + " deleted with associated task " + task)
    else:
        print("Activity was inert")
    pass
