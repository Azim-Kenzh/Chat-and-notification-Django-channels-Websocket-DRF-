from django.shortcuts import render
# from rest_framework import viewsets, mixins
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
#
#
# from chat.serializer import *
# from chat.utils import broadcast_to_groups
#
#
def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
#
#
# # class ChatViewSet(viewsets.ModelViewSet):
# #     queryset = Chat.objects.all()
# #     serializer_class = ChatSerializer
#
#
# class ChatUserViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = MyUser.objects.all()
#     serializer_class = ChatUserSerializer
#
#
# class MessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticated, ]
#
#     def perform_create(self, serializer):
#         chat = Chat.objects.get(pk=self.kwargs.get('chat_id'))
#         message = serializer.save(sender=self.request.user, chat=chat)
#         to_user = chat.get_interlocutor(self.request.user)
#         broadcast_to_groups(f'chat_{chat.id}_{to_user.id}', 'chat_message',
#                             {'event': NEW_MESSAGE,
#                              'message': MessageSerializer(message, context={'request': self.request}).data})
#         broadcast_to_groups(f'chat_{chat.id}_{self.request.user.id}', 'chat_message',
#                             {'event': NEW_MESSAGE,
#                              'message': MessageSerializer(message, context={'request': self.request}).data})
#
#
# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer


# from dateutil.parser import isoparse
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes, \
    renderer_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from chat.serializer import MessageSerializer, ChatSessionSerializer, \
    MessageFileSerializer, ChatSessionDeatilSerializer
from chat.consumers import NEW_MESSAGE
from chat.models import ChatSession, Message
from chat.utils import broadcast_to_groups
# from apps.core.utils import CustomJsonRenderer
from notification.permissions import IsChatUser

User = get_user_model()


class ChatMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, IsChatUser)
    # renderer_classes = (CustomJsonRenderer,)

    def get_queryset(self):
        chat = ChatSession.objects.get(id=self.kwargs.get('pk'))
        other_side = chat.get_interlocutor(self.request.user)
        if other_side.user_blocks.filter(blocked_user=self.request.user).exists():
            raise PermissionDenied(detail='User is blocked')
        timestamp = self.request.query_params.get('timestamp')
        queryset = super().get_queryset().filter(chat_id=self.kwargs.get('pk'))
        if timestamp:
            return queryset.filter(timestamp__lt=timestamp).order_by('-pk')

        return queryset.order_by('-pk')


class UserChatsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (CustomJsonRenderer,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        search = self.request.query_params.get('search')
        chats = self.get_queryset().\
            filter(Q(owner=self.request.user) | Q(other_side=self.request.user))
        if search:
            chats = chats.filter(Q(owner__fullname__icontains=search) |
                                 Q(other_side__fullname__icontains=search))
        chats = chats.annotate(
            last_message=Max('messages__timestamp'),
            unread_count=Count('messages', filter=Q(messages__read=False) & ~Q(messages__sender=self.request.user))
        ).order_by('-last_message')
        serializer = self.get_serializer(
            chats, many=True, context={'request': request}
        )
        return Response(data=serializer.data)


class MessageImagesViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Message.objects.all()
    # serializer_class = MessageImageSerializer
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (CustomJsonRenderer,)

    def perform_create(self, serializer):
        chat = ChatSession.objects.get(pk=self.kwargs.get('chat_id'))
        message = serializer.save(sender=self.request.user, chat=chat)
        to_user = chat.get_interlocutor(self.request.user)
        broadcast_to_groups(f'chat_{chat.id}_{to_user.id}', 'chat_message',
                            {'event': NEW_MESSAGE, 'message': MessageSerializer(message, context={'request': self.request}).data})
        broadcast_to_groups(f'chat_{chat.id}_{self.request.user.id}', 'chat_message',
                            {'event': NEW_MESSAGE, 'message': MessageSerializer(message, context={'request': self.request}).data})


class MessageFilesViewSet(MessageImagesViewSet):
    serializer_class = MessageFileSerializer


@api_view()
# @renderer_classes([CustomJsonRenderer])
@permission_classes((IsAuthenticated,))
def get_chat_for_user(request, user_id):
    user = User.objects.get(id=user_id)
    chat = ChatSession.objects.get_or_create_by_users(request.user, user)
    other_side = chat.get_interlocutor(request.user)
    if other_side.user_blocks.filter(blocked_user=request.user).exists():
        return Response({'detail': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ChatSessionDeatilSerializer(chat, context={'request': request})
    return Response(data=serializer.data)