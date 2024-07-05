import asyncio
import base64
import json
import os
import traceback
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from .models import Activity, Users, Component, Machine, Schedule, Task, Status, Report


class MyConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.length = 0
        self.image = []
        self.audio = []
        self.text = []
        self.userid = int()
        self.user = None

    async def connect(self):
        print("channel name", self.channel_name)
        print(self.scope['url_route']['kwargs']['userid'])
        room_name = self.scope['url_route']['kwargs']['userid']
        self.group_name = f"chat_{room_name}"
        if room_name != "userid":
            user = await self.getUser(int(room_name))
            self.user = user
            self.userid = int(room_name)
            print(user)
            if user.user_mode == 'A':
                await self.channel_layer.group_add(
                    "admin",
                    self.channel_name
                )
                print("admin group created...")
            elif user.user_mode == 'B':
                await self.channel_layer.group_add(
                    "inspectors",
                    self.channel_name
                )
                print("inspector group created...")
        await self.channel_layer.group_add(
            "broadcast",
            self.channel_name
        )
        self.userid = room_name
        print(self.group_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(
            "broadcast",
            self.channel_name
        )
        await self.channel_layer.group_discard(
            "admin",
            self.channel_name
        )

    async def receive(self, text_data):
        # print("receive function", text_data)
        string_dict = json.loads(text_data)
        if 'type' in string_dict:
            json_string = json.dumps(text_data)
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat.message',
                'message': json_string
            })
        elif 'token' in string_dict:
            if self.user is not None:
                print("user is not None")
                await self.saveUser(string_dict['token'])
            else:
                print("user id None")
        elif 'auth' in string_dict:
            await self.auth(event=string_dict)
        elif 'activity' in string_dict and 'create' not in string_dict and 'update' not in string_dict and 'delete' not in string_dict:
            await self.getActivity(event=string_dict)
        elif 'machine' in string_dict:
            print("condition working")
            await self.getMachine(queries="machine")
        elif 'schedule' in string_dict:
            await self.getSchedule(queries="schedule")
        elif 'component' in string_dict:
            await self.getComponent(queries="component")
        elif 'create' in string_dict:
            await self.createActivity(data=string_dict)
        elif 'users' in string_dict:
            await self.getUsers(query=string_dict)
        elif 'update' in string_dict:
            await self.updateActivity(query=string_dict)
        elif 'delete' in string_dict:
            print("delete condition worked ")
            await self.deleteActivity(query=string_dict)
        elif 'task' in string_dict:
            await self.sendTask(query=string_dict)
        elif 'report' in string_dict:
            data = base64.b64decode(string_dict['report']['content'])
            name = str(string_dict['report_id']) + str(string_dict['report']['id'])
            if string_dict['report']['id'] == 0 and string_dict['report']['uploaded'] < 1024:
                print("reinitializing... ")
                self.image = []
                self.audio = []
                self.text = []
            if string_dict['report']['type'] == 'image':
                file_path = self.handleImage(data=data, name=name)
                if file_path not in self.image:
                    self.image.append(file_path)
            elif string_dict['report']['type'] == 'audio':
                file_path = self.handleAudio(data=data, name=name)
                if file_path not in self.audio:
                    self.audio.append(file_path)
                pass
            elif string_dict['report']['type'] == 'text':
                self.text.append(data.decode('utf-8'))
                print("text type data received", data.decode('utf-8'))
                pass
            print(string_dict['report']['size'], string_dict['report']['uploaded'], string_dict['user_id'],
                  string_dict['report']['id'], string_dict['task_id'], len(data))
            if string_dict['report']['size'] == string_dict['report']['uploaded'] + len(data):
                print("finish receiving file...")
                print(dict(string_dict).keys())
                if string_dict['report']['id'] == string_dict['total_item']:
                    await self.saveReport(user_id=string_dict['user_id'],
                                          task_id=string_dict['task_id'])
                else:
                    print("item count ", string_dict['report']['id'], string_dict['total_item'])
        elif 'report-get' in string_dict:
            full = False
            if string_dict['report-get'] == -1:
                full = True
            await self.sendReport(string_dict, full)
        elif 'file-get' in string_dict:
            print(string_dict['file-get'])
            await self.sendFile(string_dict)
        else:
            await self.fetchPage(data_dict=string_dict)

    @database_sync_to_async
    def saveUser(self, token):
        self.user.token = token
        print("token is...", self.user.token)
        self.user.save()

    @database_sync_to_async
    def saveReport(self, task_id, user_id):
        # print('saveReport', type(self.text[0]), type(self.image[0]), type(self.audio[0]))
        activity = Activity.objects.filter(
            activity_id=Task.objects.filter(task_id=task_id).first().task_activity_id.activity_id).first()
        report = Report(
            report_activity=activity,
            report_data={
                "image": self.image,
                "audio": self.audio,
                "text": self.text
            },
            report_user_id=Users.objects.filter(user_id=user_id).first()
        )
        report.save()
        activity.activity_status_id = Status.objects.filter(status_id=4).first()
        activity.save()

    def handleImage(self, data, name):
        media_directory = 'files'
        file_name = str(name) + ".jpg"
        file_path = os.path.join(settings.MEDIA_ROOT, media_directory, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'ab') as file:
            file.write(data)
            file.flush()
        return file_path

    async def chat_message(self, event):
        await self.send(text_data=event['message'])

    @database_sync_to_async
    def deleteActivity(self, query):
        query = json.loads(query)
        print("activity is going to delete")
        activity = Activity.objects.filter(activity_id=query['activity']['activity_id']).first()
        if activity is not None:
            print("activity is not none")
            activity.delete()
        else:
            print("couldn't find activity")
        asyncio.run(self.send(text_data=json.dumps({"callback": "delete", "model": "Activity"})))

    async def auth(self, event):
        result = await self.checkAuth(event=event)  # Use self.checkAuth instead of checkAuth
        if result["usermode"] == "A":
            self.channel_layer.group_add(
                "admin",
                self.channel_name
            )
            print("group created admin")
        elif result["usermode"] == "B":
            self.channel_layer.group_add(
                "user",
                self.channel_name
            )
            print("group created user")
        await self.send(text_data=json.dumps(result))

    async def getActivity(self, event):
        queries = await self.existing()
        await self.sendActivity(queries=queries)

    @database_sync_to_async
    def getUser(self, id):
        return Users.objects.filter(user_id=id).get()

    @database_sync_to_async
    def checkAuth(self, event):
        username = event['username']
        password = event['password']
        result = {
            'user_id': 'None',
            'username': 'None',
            'password': 'None',
            'usermode': 'None'
        }
        try:
            user = Users.objects.get(user_name=username, user_password=password)
            mode = user.user_mode
            result = {
                'user_id': user.user_id,
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
                    "activity_last_reported": query.activity_last_reported.strftime("%Y-%m-%d"),
                    "assigned_to": task.task_assign_to.user_id,
                    "schedule_value": query.activity_schedule_value,
                    "assigned_to_user": task.task_assign_to.user_name if task is not None else "None",
                    "activity_creator": Users.objects.filter(user_id=query.activity_creator.user_id).first().user_name,
                    "change": "create",
                    "ui_change": "create"
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
                    "activity_last_reported": query.activity_last_reported.strftime("%Y-%m-%d"),
                    "assigned_to": 0,
                    "schedule_value": query.activity_schedule_value,
                    "activity_creator": Users.objects.filter(user_id=query.activity_creator.user_id).first().user_name,
                    "assigned_to_user": "None",
                    "change": "create",
                    "ui_change": "create"
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
    def createActivity(self, data):
        print(data)
        str = "failed"
        instance = Activity(
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
                schedule_id=data['activity']['activity_schedule_id']
            ).first(),
            activity_creator=Users.objects.all().filter(user_name=data['username'],
                                                        user_password=data['password']
                                                        ).first(),
            activity_schedule_value=data['activity']['schedule_value']
        )
        instance.save()
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
            "schedule_value": instance.activity_schedule_value,
            "activity_creator": instance.activity_creator.user_name,
            "assigned_to": 0,
            "assigned_to_user": "None",
            "change": "create",
            "ui_change": "create"
        }
        mess = {
            "callback": "activity created",
            "modal": "Activity"
        }
        asyncio.run(self.send(text_data=json.dumps(mess)))
        asyncio.run(self.send(text_data=json.dumps(body)))

    @database_sync_to_async
    def getUsers(self, query):
        print(query['users'])
        users = Users.objects.filter(user_name__startswith=query['users'], user_mode='B').order_by('user_name')
        print(len(users))
        usersBody = []
        for user in users:
            body = {
                'username': user.user_name,
                'userid': user.user_id,
                'key': query['users']
            }
            usersBody.append(body)
            print(body)
        asyncio.run(self.send(text_data=json.dumps(usersBody)))
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

    async def send_database_client(self, body):
        print(json.dumps(body["message"]))
        await self.send(text_data=json.dumps(body))
        pass

    @database_sync_to_async
    def updateActivity(self, query):
        print("update activity called")
        print(type(query),query['activity']['activity_id'])
        try:
            activity = Activity.objects.filter(
                activity_id=int(query['activity']['activity_id'])
            ).first()
            activity.activity_name = query['activity']['activity_name']
            activity.activity_description = query['activity']['activity_description']
            activity.activity_component_id = Component.objects.filter(
                component_id=query['activity']['activity_component_id']).first()
            activity.activity_machine_id = Machine.objects.filter(
                machine_id=query['activity']['activity_machine_id']).first()
            activity.activity_schedule_id = Schedule.objects.filter(
                schedule_id=query['activity']['activity_schedule_id']).first()
            task = Task.objects.filter(
                task_activity_id=query['activity']['activity_id']
            ).first()

            if query['activity']['assigned_to_user'] == "None":
                if activity is not None:
                    if task is not None:
                        print("task is not none and activity is not none")
                        activity.activity_status_id = Status.objects.filter(status_id=1).first()
                        activity.save()
                    else:
                        print("task not assigned for this activity")
                        activity.save()
                else:
                    print("creating Activity because no activity found")
                    self.createActivity(data=query)
                    pass
            else:
                activity.activity_status_id = Status.objects.filter(
                    status_id=2
                ).first()
                task = Task(
                    task_assign_to=Users.objects.filter(user_id=query['activity']['activity_assigned_to']).first(),
                    task_activity_id=activity
                )

                activity.save()
                task.save()
                asyncio.run(self.send(text_data=json.dumps({'callback': 'created', 'model': 'task'})))
        except Exception as e:
            print("Exception occurred at line", traceback.format_exc())

    async def send_database_change_delete(self, body):
        await self.send(text_data=json.dumps(body))

    @database_sync_to_async
    def sendTask(self, query):
        print("send task function working...")
        task = Task.objects.filter(
            task_assign_to=Users.objects.filter(
                user_id=query['user_id']
            ).first()).order_by("task_id")
        for row in task:
            body = {
                "task_id": row.task_id,
                "activity_id": row.task_activity_id.activity_id,
                "activity_assigned_by": row.task_activity_id.activity_creator.user_name,
                "activity_name": row.task_activity_id.activity_name,
                "activity_description": row.task_activity_id.activity_description,
                "activity_issued": row.task_activity_id.activity_issued_date.isoformat()
            }
            print(body)
            asyncio.run(self.send(text_data=json.dumps(body)))
        pass

    def handleAudio(self, data, name):
        media_directory = 'files'
        file_name = str(name) + "audio.mp3"
        file_path = os.path.join(settings.MEDIA_ROOT, media_directory, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'ab') as file:
            file.write(data)
            file.flush()
        return file_path

    @database_sync_to_async
    def sendReport(self, string_dict, full):
        if full:
            activities = Activity.objects.all()
            for activity in activities:
                reports = Report.objects.filter(
                    report_activity=activity,
                ).all()
                if reports is not None:
                    for report in reports:
                        print(report.report_data)
                        user = Users.objects.filter(user_id=report.report_user_id.user_id).first()
                        asyncio.run(self.send(text_data=json.dumps({
                            'activity-id': activity.activity_id,
                            'activity-name': activity.activity_name,
                            'activity-description': activity.activity_description,
                            'report_from': user.user_name,
                            'report_user_id': user.user_id,
                            'reports-all': report.report_data
                        })))
                else:
                    print("No Report for this activity...")
        else:
            print("called sendReport...")
            activity = Activity.objects.filter(activity_id=string_dict['report-get']).first()
            print(activity)
            reports = Report.objects.filter(
                report_activity=activity,
            )
            print(reports)
            for report in reports:
                user = Users.objects.filter(user_id=report.report_user_id.user_id).first()
                asyncio.run(self.send(text_data=json.dumps({
                    'report_from': user.user_name,
                    'report_user_id': user.user_id,
                    'reports': report.report_data
                })))
            pass

    async def sendFile(self, string_dict):
        print(string_dict, "sending file...")
        if os.path.exists(string_dict['file-get']):
            file_size = os.path.getsize(string_dict['file-get'])
            await self.send(text_data=json.dumps({"file-size": file_size}))
            with open(string_dict['file-get'], 'rb') as file:  # Open the file in binary mode
                chunk_size = 1024
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    await self.send(bytes_data=chunk)  # Use bytes_data instead of text_data
        pass
