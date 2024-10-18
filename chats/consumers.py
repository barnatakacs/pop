from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Message, User, Chat
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

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
        text_data_json = json.loads(text_data)
        message_content = text_data_json['content']

        user = self.scope['user']
        chat = self.chat_id

        await self.save_message(user, chat, message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': message_content,
                'user': self.scope['user'].username,
                'created_at': self.now(),
            }
        )

    async def chat_message(self, event):
        message = event['content']
        user = event['user']
        created_at = event['created_at']

        await self.send(text_data=json.dumps({
            'content': message,
            'user': user,
            'created_at': created_at,
        }))

    def now(self):
        return datetime.now().strftime("%B %d, %Y, %I:%M %p")

    @sync_to_async
    def save_message(self, user, chat, message):
        chat = Chat.objects.get(id=chat)

        Message.objects.create(chat=chat, user=user, content=message)
