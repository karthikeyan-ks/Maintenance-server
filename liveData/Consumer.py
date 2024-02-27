import asyncio
import json

import channels.layers
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import traceback
from .models import Activity, Users, Component, Machine, Schedule, Task, Status


class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None

    async def connect(self):
        print("channel name", self.channel_name)
        # self.scope['url_route']['kwargs']['room_name']
        print(self.scope['url_route']['kwargs'])
        room_name = "users"

        # Construct a group name based on the room name
        self.group_name = f"chat_{room_name}"
        print(self.group_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print(text_data)
        string_dict = json.loads(text_data)
        if 'type' in string_dict:
            # Serialize the data to a JSON-formatted string
            json_string = json.dumps(text_data)
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat.message',
                'message': json_string
            })
        elif 'auth' in string_dict:
            await self.auth(event=string_dict)
        elif 'activity' in string_dict and 'create' not in string_dict and 'update' not in string_dict:
            await self.getActivity(event=string_dict)
        elif 'machine' in string_dict:
            print("condition working")
            await self.getMachine(queries="machine")
        elif 'schedule' in string_dict:
            await self.getSchedule(queries="schedule")
        elif 'component' in string_dict:
            await self.getComponent(queries="component")
        elif 'create' in string_dict:
            await self.creatActivity(data=string_dict)
        elif 'users' in string_dict:
            await self.getUsers(query=string_dict)
        elif 'update' in string_dict:
            await self.updateActivity(query=string_dict)
        else:
            await self.fetchPage(data_dict=string_dict)

    async def chat_message(self, event):
        await self.send(text_data=event['message'])

    async def auth(self, event):
        result = await self.checkAuth(event=event)  # Use self.checkAuth instead of checkAuth
        if result["usermode"] == "A":
            self.channel_layer.group_add(
                "admin",
                self.channel_name
            )
            print("group created admin")
        elif result["usermode"] == "B":
            self.channel_name.group_add(
                "user",
                self.channel_name
            )
            print("group created user")
        await self.send(text_data=json.dumps(result))

    async def getActivity(self, event):
        queries = await self.existing()
        await self.sendActivity(queries=queries)

    @database_sync_to_async
    def checkAuth(self, event):
        username = event['username']
        password = event['password']
        result = 0
        try:
            user = Users.objects.get(user_name=username, user_password=password)
            mode = user.user_mode
            result = {
                'username': user.user_name,
                'password': user.user_password,
                'usermode': user.user_mode
            }
        except Users.DoesNotExist:
            print("User does not exist.")
        return result

    @database_sync_to_async
    def existing(self):
        print("activity are fetching")
        queries = Activity.objects.all().order_by('activity_id')
        activities = []
        for query in queries:
            task = Task.objects.filter(
                task_activity_id=Activity.objects.filter(activity_id=query.activity_id).first()
            ).first()
            if task is not None:
                print(task)
                body = {
                    "activity_id": query.activity_id,
                    "activity_descrption": query.activity_description,
                    "actvity_status_id": query.activity_status_id.status_id,
                    "activity_component_id": query.activity_component_id.component_id,
                    "activity_machine_id": query.activity_machine_id.machine_id,
                    "activity_schedule_id": query.activity_schedule_id.schedule_id,
                    "activity_name": query.activity_name,
                    "activity_issued_date": query.activity_issued_date.strftime("%Y-%m-%d"),
                    "assigned_to": task.task_assign_to.user_id,
                    "assigned_to_user": task.task_assign_to.user_name,
                    "activity_creator": Users.objects.filter(user_id=query.activity_creator.user_id).first().user_name,
                    "change": "create"
                }
                activities.append(body)
            else:
                body = {
                    "activity_id": query.activity_id,
                    "activity_descrption": query.activity_description,
                    "actvity_status_id": query.activity_status_id.status_id,
                    "activity_component_id": query.activity_component_id.component_id,
                    "activity_machine_id": query.activity_machine_id.machine_id,
                    "activity_schedule_id": query.activity_schedule_id.schedule_id,
                    "activity_name": query.activity_name,
                    "activity_issued_date": query.activity_issued_date.strftime("%Y-%m-%d"),
                    "assigned_to": 0,
                    "activity_creator": Users.objects.filter(user_id=query.activity_creator.user_id).first().user_name,
                    "assigned_to_user": "None",
                    "change": "create"
                }
                activities.append(body)
        return activities

    async def sendActivity(self, queries):
        for query in queries:
            await self.send(text_data=json.dumps(query))

    @database_sync_to_async
    def getMachine(self, queries):
        print("machines are fetching")
        queries = Machine.objects.all().order_by("machine_id")
        for query in queries:
            body = {
                "id": query.machine_id,
                "name": query.machine_name,
                "type": "machine"
            }
            asyncio.run(self.send(text_data=json.dumps(body)))

    @database_sync_to_async
    def getComponent(self, queries):
        queries = Component.objects.all().order_by("component_id")
        for query in queries:
            body = {
                "id": query.component_id,
                "name": query.component_name,
                "type": "component"
            }
            asyncio.run(self.send(text_data=json.dumps(body)))

    @database_sync_to_async
    def getSchedule(self, queries):
        queries = Schedule.objects.all().order_by("schedule_id")
        for query in queries:
            body = {
                "id": query.schedule_id,
                "name": query.schedule_type,
                "type": "schedule",
                "value": query.schedule_value,
                "current": query.schedule_current_value
            }
            print(query.schedule_id)
            asyncio.run(self.send(text_data=json.dumps(body)))

    @database_sync_to_async
    def creatActivity(self, data):
        print(data)
        str = "failed"
        new_instance = Activity(
            activity_issued_date=datetime.now().date(),
            activity_name=data['activity']['activity_name'],
            activity_description=data['activity']['activity_description'],
            activity_machine_id=Machine.objects.all().filter(
                machine_id=data['activity']['activity_machine_id']
            ).first(),
            activity_component_id=Component.objects.all().filter(
                component_id=data['activity']['activity_component_id']
            ).first(),
            activity_schedule_id=Schedule.objects.all().filter(
                schedule_id=data['activity']['activity_component_id']
            ).first(),
            activity_creator=Users.objects.all().filter(user_name=data['username'],
                                                        user_password=data['password']
                                                        ).first()
        )
        new_instance.save()
        mess = {
            "callback": "activity created",
            "modal": "Activity"
        }
        asyncio.run(self.send(text_data=json.dumps(mess)))

    @database_sync_to_async
    def getUsers(self, query):
        print(query['users'])
        users = Users.objects.filter(user_name__startswith=query['users'], user_mode='B').order_by('user_name')
        print(len(users))
        for user in users:
            body = {
                'username': user.user_name,
                'userid': user.user_id,
                'key': query['users']
            }
            print(body)
            asyncio.run(self.send(text_data=json.dumps(body)))
        pass

    @database_sync_to_async
    def create(self, query):
        querySet = {}
        type_str = ""

        if query == "component":
            body = Component.objects.all().order_by('component_id')
            type_str = "component"
            for q in body:
                querySet[q.component_id] = {
                    'component_name': q.component_name,
                    'component_id': q.component_id
                }
        elif query == "machine":
            body = Machine.objects.all().order_by('machine_id')
            type_str = "machine"
            for q in body:
                querySet[q.machine_id] = {
                    'machine_id': q.machine_id,
                    'machine_name': q.machine_name
                }
        elif query == "schedule":
            body = Schedule.objects.all().order_by('schedule_id')
            type_str = "schedule"
            for q in body:
                querySet[q.schedule_id] = {
                    'schedule_id': q.schedule_id,
                    'schedule_name': q.schedule_type
                }
        else:
            return "unrecognizable query"
        querySet.update({'page': 'create'})
        querySet.update({'type': type_str})
        return querySet

    pass

    def send_data_on_database_change(self, instance):
        task = Task.objects.filter(
            task_activity_id=Activity.objects.filter(activity_id=instance.activity_id).first()
        )
        body = {
            "activity_id": instance.activity_id,
            "activity_descrption": instance.activity_description,
            "actvity_status_id": instance.activity_status_id.status_id,
            "activity_component_id": instance.activity_component_id.component_id,
            "activity_machine_id": instance.activity_machine_id.machine_id,
            "activity_schedule_id": instance.activity_schedule_id.schedule_id,
            "activity_name": instance.activity_name,
            "activity_issued_date": instance.activity_issued_date.strftime("%Y-%m-%d"),
            "assigned_user": task.task_assign_to.user_id
        }
        channels_layer = channels.layers.get_channel_layer()
        asyncio.run(self.send_data_to_client(channels_layer, body))
        pass

    async def send_database_client(self, body):
        await self.send(text_data=json.dumps(body))
        pass

    import traceback

    @database_sync_to_async
    def updateActivity(self, query):
        try:
            activity = Activity.objects.filter(
                activity_id=query['activity']['activity_id']
            ).first()
            if activity is not None:  # Check if activity is not None
                print(activity)
                if activity.activity_status_id != Status.objects.filter(status_id=2).first():
                    activity.activity_status_id = Status.objects.filter(status_id=2).first()
                    activity.save()
                    task = Task(
                        task_assign_to=Users.objects.filter(user_id=query['activity']['activity_assigned_to']).first(),
                        task_activity_id=Activity.objects.filter(activity_id=query['activity']['activity_id']).first()
                    )
                    task.save()
                    print("task created")
                else:
                    task = Task.objects.filter(
                        task_activity_id=activity.activity_id
                    ).first()
                    task.task_assign_to = Users.objects.filter(
                        user_id=query['activity']['activity_assigned_to']).first()
                    task.save()
                    print("task changed ")
            else:
                print("No activity found with activity_id:", query['activity']['activity_id'])
        except Exception as e:
            print("Exception occurred at line", traceback.format_exc().splitlines()[-1])
            print("Exception details:", e)
        asyncio.run(self.send(text_data=json.dumps({'callback': 'created', 'model': 'Task'})))
