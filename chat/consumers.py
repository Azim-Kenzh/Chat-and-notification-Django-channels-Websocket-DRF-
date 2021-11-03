import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import Q

from .serializer import MessageSerializer
from .models import Message, ChatSession, ChatStatus, Notification
# from notification.models import PushNotification

User = get_user_model()


NEW_MESSAGE = 'new_message'
# READ_CHAT = 'read_chat'
# READ_FORUM = 'read_forum'


@database_sync_to_async
def get_chat(current_user, user_id):
    chat = ChatSession.objects.filter(Q(owner=int(user_id), user=current_user) | Q(user=int(user_id), owner=current_user)).select_related('owner', 'other_side').first()
    user = chat.get_interlocutor(current_user)
    if current_user.user_blocks.filter(blocked_user=user).exists():
        return user, None
    return user, chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_side, self.chat = await get_chat(self.scope['user'],
                                                    self.scope['url_route']['kwargs']['user_id'])
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
        await update_chat_status(self.chat, self.scope['user'], True)

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await update_chat_status(self.chat, self.scope['user'], False)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        response_data = None

        chat_is_open = await check_chat_status(self.scope['user'], self.chat)
        response_data = await create_message(
            self.scope['user'],
            self.chat,
            data['text'],
        )
        response_data = {'event': data['event'], "message": response_data}
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'data': response_data,
            }
        )
        if chat_is_open:
            # chat is open, send new message
            await self.channel_layer.group_send(
                self.interlocutor_group,
                {
                    'type': 'chat_message',
                    'data': response_data,
                }
            )
        else:
            # chat is closed, so create and send notification about new message
            await create_notification()
            await self.channel_layer.group_send(
                f'user_{self.scope["user"].id}',
                {
                    'type': 'notify',
                    'data': response_data,
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
def create_notification(user, chat):
    message = Notification.objects.create(chat=chat, user=user)
    return MessageSerializer(message).data


@database_sync_to_async
def mark_as_read(user, other_side, chat):
    messages = Message.objects.filter(sender=other_side, chat_id=chat)
    messages.update(read=True)
    # mark message related notifications as read
    # PushNotification.objects.filter(recipient=user, read=False,
    #                                 object_id=str(other_side.id)).update(read=True)
    if messages:
        return messages.last().id
    else:
        return None


@database_sync_to_async
def update_chat_status(user, chat, is_current):
    chat_status = ChatStatus.objects.get_or_create(chat=chat, user=user)
    chat_status.current = is_current
    chat_status.save()


@database_sync_to_async
def check_chat_status(user, chat):
    chat_status = ChatStatus.objects.get_or_create(chat=chat, user=user)
    return chat_status.current


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f'user_{self.scope["user"].id}'  # group for user to send notifications

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        # await update_chat_status(self.chat, self.scope['user'], True)  # maybe show as online?

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        # await update_chat_status(self.chat, self.scope['user'], False)  # maybe show as offline?

    # Receive message from room group
    async def notify(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
