from django.db import models
from django.db import connection
from django.utils import timezone
from django.core.validators import MinLengthValidator


# Create your models here


class Demo(models.Model):
    demo_id = models.CharField(max_length=30)


class Machine(models.Model):
    machine_name = models.CharField(max_length=50)
    machine_id = models.IntegerField(primary_key=True)


class Component(models.Model):
    component_name = models.CharField(max_length=50)
    component_id = models.IntegerField(primary_key=True)


class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    schedule_type = models.CharField(max_length=10)
    schedule_value = models.IntegerField(default=7)


class Status(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=30)


class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=30)
    activity_issued_date = models.DateField(default=timezone.now)
    activity_description = models.TextField()
    activity_machine_id = models.ForeignKey(Machine, on_delete=models.CASCADE)
    activity_component_id = models.ForeignKey(Component, on_delete=models.CASCADE)
    activity_schedule_id = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    activity_status_id = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)


class ChangeType(models.Model):
    change_type_id = models.IntegerField(primary_key=True)
    change_type = models.CharField(max_length=30)


class ChangeSeeker(models.Model):
    ChangeSeeker_id = models.AutoField(primary_key=True)
    Changed_activity_id = models.IntegerField()
    change_activity_type_id = models.ForeignKey(ChangeType, on_delete=models.CASCADE, default=1)
    position_number = models.IntegerField(default=0)


class Users(models.Model):
    class YourChoices(models.TextChoices):
        CHOICE_ONE = 'A', 'administrator'
        CHOICE_TWO = 'B', 'inspector'

    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30, unique=True)
    user_password = models.CharField(max_length=15, validators=[MinLengthValidator(5)])
    user_mode = models.CharField(
        max_length=1,
        choices=YourChoices.choices,
        default=YourChoices.CHOICE_TWO
    )


class Task(models.Model):
    task_assign_to = models.ForeignKey(Users, on_delete=models.CASCADE)
    task_activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    task_id = models.AutoField(primary_key=True)


class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    report_text = models.TextField()
    report_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, default=1)
