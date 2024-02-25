import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Activity


@receiver(post_save, sender=Activity)
def on_database_change(sender, instance, created, **kwargs):
    print("triggered")
    channels_layer = channels.layers.get_channel_layer()
    body = {
        "activity_id": instance.activity_id,
        "activity_descrption": instance.activity_description,
        "actvity_status_id": instance.activity_status_id.status_id,
        "activity_component_id": instance.activity_component_id.component_id,
        "activity_machine_id": instance.activity_machine_id.machine_id,
        "activity_schedule_id": instance.activity_schedule_id.schedule_id,
        "activity_name": instance.activity_name,
        "activity_issued_date": instance.activity_issued_date.strftime("%Y-%m-%d"),
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
