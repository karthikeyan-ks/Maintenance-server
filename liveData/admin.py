from django.contrib import admin
from .models import Activity, Report, Status, Machine, Component, Schedule, ChangeSeeker, ChangeType, Users, Demo, Task

# Register your models here.
admin.site.register([Activity, Report, Status, Machine, Component, Schedule, ChangeSeeker, ChangeType, Users, Demo, Task])
