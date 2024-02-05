from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Activity,Task,Report,Users,Component,Machine,Schedule

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.channel_name)
        #self.scope['url_route']['kwargs']['room_name']
        room_name = "users"

        # Construct a group name based on the room name
        self.group_name = f"chat_{room_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()




    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    
    
    
    async def receive(self,text_data):
        string_dict = json.loads(text_data)
        if 'type' in text_data:
            # Serialize the data to a JSON-formatted string
            json_string = json.dumps(text_data)
            await self.channel_layer.group_send(self.group_name,{
                'type': 'chat.message',
                'message': json_string
            })
        else:
            await self.fetchPage(data_dict=string_dict)
        
        
        
    async def chat_message(self, event):
        await self.send(text_data=event['message'])
        
        
        
        
    async def fetchPage(self, data_dict):
        page=data_dict['page']
        query=data_dict['query']
        if page =='existing':
            print("calling existinbg")
            result=await self.existing(query=query)
            print(result)
            await self.send(text_data=json.dumps(result))
        elif page == 'create':
            result=await self.create(query=query)
            await self.send(text_data=json.dumps(result))
        elif page == 'pending':
            await self.pending(query=query)
        elif page == 'review':
            await self.review(query=query)
        elif page== 'create activity':
            print(data_dict)
            result=await self.creatActivity(data_dict)
            text_data = f'{{"page":"create","type":"activity","result":"{result}"}}'
            await self.send(text_data=text_data)
        else:
            await self.unknown(query=query)
    
    
    @database_sync_to_async
    def existing(self,query):
        body=[]
        querys=Activity.objects.all().filter(activity_status_id=2).order_by('activity_id')
        for query in querys:
            body.insert({
                "activity_id":query.activity_id,
                "activity_descrption":query.activity_description,
                "actvity_status_id":query.activity_status_id,
                "activity_component_id":query.activity_component_id,
                "activity_machine_id":query.activity_machine_id,
                "activity_machine_id":query.activity_schedule_id,
                "activity_name":query.activity_name,
                "activity_issued_date":query.activity_issued_date
                })
        return body
    
    @database_sync_to_async
    def creatActivity(self,data):
        print(data)
        str="failed"
        new_instance=Activity(activity_name=data['name'],
            activity_description=data['description'],
            activity_machine_id=Machine.objects.all().filter(machine_id=data['machine_id']).first(),
            activity_component_id=Component.objects.all().filter(component_id=data['component_id']).first(),
            activity_schedule_id=Schedule.objects.all().filter(schedule_id=data['schedule_id']).first()
            )
        new_instance.save()
        str='ok'
        return str
    
    
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
        querySet.update({'page':'create'})
        querySet.update({'type':type_str})
        return querySet

    
    
    
    @database_sync_to_async
    def pending(self,query):
        body=[]
        return body
        
    
    
    
    async def review(self,query):
        await self.send(text_data=query)
        pass
    
    
    
    
    async def unknown(self,query):
        await self.send(text_data=query)
        pass

        