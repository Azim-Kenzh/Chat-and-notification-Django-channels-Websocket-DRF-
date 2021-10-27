# # chat/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))



"""----------------------------------------------------------------------------"""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .serializer import MessageSerializer
from .models import Message, ChatSession
from notification.models import PushNotification

User = get_user_model()


TYPING = 'typing'
NEW_MESSAGE = 'new_message'
MESSAGE_READ = 'message_read'


@database_sync_to_async
def get_chat(current_user, chat_id):
    chat = ChatSession.objects.filter(pk=int(chat_id)).select_related('owner', 'other_side').first()
    user = chat.get_interlocutor(current_user)
    if current_user.user_blocks.filter(blocked_user=user).exists():
        return user, None
    return user, chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_side, self.chat = await get_chat(self.scope['user'],
                                                    self.scope['url_route']['kwargs']['chat_id'])
        if self.chat is None:  # the other side is blocked by user
            await self.disconnect()
        self.group_name = f'chat_{self.chat.id}_{self.scope["user"].id}'       # group for user
        self.interlocutor_group = f'chat_{self.chat.id}_{self.other_side.id}'  # group for interlocutor

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        sending_data = None
        if data['event'] == TYPING:
            sending_data = {"chat_id": self.chat.id, **data}

        elif data['event'] == MESSAGE_READ:
            message_id = await mark_as_read(
                self.scope['user'],
                self.other_side,
                self.chat
            )
            sending_data = {"chat_id": self.chat.id, 'message_id': message_id, **data}

        elif data['event'] == NEW_MESSAGE:
            sending_data = await create_message(
                self.scope['user'],
                self.chat,
                data['text']
            )
            sending_data = {'event': data['event'], "message": sending_data}
        if sending_data['event'] == NEW_MESSAGE:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'data': sending_data,
                }
            )
        await self.channel_layer.group_send(
            self.interlocutor_group,
            {
                'type': 'chat_message',
                'data': sending_data,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))


@database_sync_to_async
def create_message(sender, chat, text):
    message = Message.objects.create(chat=chat, sender=sender, text=text)
    return MessageSerializer(message).data


@database_sync_to_async
def mark_as_read(user, other_side, chat):
    messages = Message.objects.filter(sender=other_side, chat_id=chat)
    messages.update(read=True)
    # mark message related notifications as read
    PushNotification.objects.filter(recipient=user, read=False,
                                    object_id=str(other_side.id)).update(read=True)
    if messages:
        return messages.last().id
    else:
        return None