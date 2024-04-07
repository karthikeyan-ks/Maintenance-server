# your_app/tasks.py
import datetime

from celery import shared_task
from .models import Activity, Status, Schedule
from django.utils import timezone
from datetime import datetime


@shared_task
def your_task_function():
    # Your code to be executed periodically
    print("Task executed!")


@shared_task
def update():
    activities = Activity.objects.all()
    for activity in activities:
        # activity.activity_schedule_value = activity.activity_schedule_value + 1
        lastReport = activity.activity_last_reported
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        diff = current_date - lastReport
        print(diff.days, current_date, lastReport)
        if activity.activity_status_id == Status.objects.filter(
                status_id=2).first() and diff.days - activity.activity_schedule_value <= 1 and activity.activity_schedule_id == Schedule.objects.filter(
                schedule_id=1).first():
            activity.activity_status_id = Status.objects.filter(status_id=3).first()
            activity.save()

        # Assuming current is a datetime.datetime object
