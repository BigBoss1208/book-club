import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from members.models import Message, ChatRoom
from asgiref.sync import sync_to_async
from django.utils import timezone

class ClubChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.club_id = self.scope['url_route']['kwargs']['club_id']
        self.room_group_name = f'club_chat_{self.club_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user_id = self.scope['user'].id
        club_id = self.club_id
        msg_obj = await self.save_message(user_id, club_id, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.content,
                'sender': msg_obj.sender.username,
                'sent_at': msg_obj.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sent_at': event['sent_at'],
        }))

    @sync_to_async
    def save_message(self, user_id, club_id, content):
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(club_id=club_id)
        return Message.objects.create(chat_room=room, sender=user, content=content)
