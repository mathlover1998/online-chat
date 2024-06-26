from channels.generic.websocket import WebsocketConsumer
from .models import *
import json
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup,group_name=self.chatroom_name)
        # add channel_layer and wrap it to be called as a async func
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name,self.channel_name
        )
        if self.chatroom.groupchat_name:
            UserChannel.objects.get_or_create(
                member = self.user, 
                group = self.chatroom,
                channel = self.channel_name 
            )

        #add or update onlines users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_conline_count()
        self.accept()


    def disconnect(self, code):
        # discard channel_layer and wrap it to be called as a async func
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,self.channel_name
        )
        if self.chatroom.groupchat_name:
            user_channel = UserChannel.objects.get(channel=self.channel_name )
            user_channel.delete()
        #add or update onlines users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_conline_count()
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # print(text_data_json)
        # body = text_data_json['body']

        message = Message.objects.create(
            body=text_data_json['message'],
            user = self.user,
            group = self.chatroom
        )
        event = {
            'type':'message_handler',
            'message_id':message.id
        }
        # send through channel_layer and wrap it to be called as a async func
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,event
        )
    
    def message_handler(self,event):
        message_id = event['message_id']
        message = Message.objects.get(id=message_id)
        context = {
            'message':message,
            'user': self.user
        }
        html = render_to_string("rtchat/partials/chat_message_p.html",context=context)
        self.send(text_data=html)

    def update_conline_count(self):
        online_count = self.chatroom.users_online.count() -1
        event = {
            'type': 'online_count_handler',
             'online_count':online_count
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,event
        )

    def online_count_handler(self,event):
        online_count = event['online_count']
        context = {
            'online_count': online_count,
            'chat_group': self.chatroom
        }
        html = render_to_string('rtchat/partials/online_count.html',context)
        self.send(text_data=html)

    # def update_member(self):
    #     pass