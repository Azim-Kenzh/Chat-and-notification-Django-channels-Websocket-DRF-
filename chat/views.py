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
from account.models import MyUser


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
from django.db.models import Q, Max, Count, OuterRef, Exists
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes, \
    renderer_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from chat.serializer import MessageSerializer, ChatUserSerializer, \
    MessageFileSerializer, ChatSessionDeatilSerializer, UpdateNotificationSerializer
from chat.consumers import NEW_MESSAGE
from chat.models import ChatSession, Message, Notification
from chat.utils import broadcast_to_groups
# from apps.core.utils import CustomJsonRenderer
from notification.permissions import IsChatUser, IsOwner

User = get_user_model()


class ChatMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, IsChatUser)
    # renderer_classes = (CustomJsonRenderer,)
    #
    # def get_queryset(self):
    #     chat = ChatSession.objects.get(id=self.kwargs.get('pk'))
    #     other_side = chat.get_interlocutor(self.request.user)
    #     if other_side.user_blocks.filter(blocked_user=self.request.user).exists():
    #         raise PermissionDenied(detail='User is blocked')
    #     # timestamp = self.request.query_params.get('timestamp')
    #     queryset = super().get_queryset().filter(chat_id=self.kwargs.get('pk'))
    #     # if timestamp:
    #     #     return queryset.filter(timestamp__lt=timestamp).order_by('-pk')
    #
    #     return queryset.order_by('-pk')


class ChatUsersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = MyUser.objects.all()
    serializer_class = ChatUserSerializer
    permission_classes = (IsAuthenticated,)
    # pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().exclude(id=request.user.id)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))

        notification = Notification.objects.select_related('chat'). \
            filter(Q(user_id=self.request.user.id, chat__owner_id=OuterRef('pk'), seen=False) |
                   Q(user_id=self.request.user.id, chat__other_side_id=OuterRef('pk'), seen=False))
        chat = ChatSession.objects. \
            filter(Q(owner_id=OuterRef('pk'), other_side_id=request.user.id) |
                   Q(other_side_id=OuterRef('pk'), owner_id=request.user.id))
        queryset = queryset.\
            annotate(has_unread=Exists(notification), chat_exists=Exists(chat)).\
            order_by('-chat_exists', 'first_name')
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )
        return Response(data=serializer.data)


# class MessageImagesViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     queryset = Message.objects.all()
#     # serializer_class = MessageImageSerializer
#     permission_classes = (IsAuthenticated,)
#     # renderer_classes = (CustomJsonRenderer,)
#
#     def perform_create(self, serializer):
#         chat = ChatSession.objects.get(pk=self.kwargs.get('chat_id'))
#         message = serializer.save(sender=self.request.user, chat=chat)
#         to_user = chat.get_interlocutor(self.request.user)
#         broadcast_to_groups(f'chat_{chat.id}_{to_user.id}', 'chat_message',
#                             {'event': NEW_MESSAGE, 'message': MessageSerializer(message, context={'request': self.request}).data})
#         broadcast_to_groups(f'chat_{chat.id}_{self.request.user.id}', 'chat_message',
#                             {'event': NEW_MESSAGE, 'message': MessageSerializer(message, context={'request': self.request}).data})

#
# class MessageFilesViewSet(MessageImagesViewSet):
#     serializer_class = MessageFileSerializer


class UpdateNotificationViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = UpdateNotificationSerializer
    permission_classes = [IsOwner, ]




@api_view()
# @renderer_classes([CustomJsonRenderer])
@permission_classes((IsAuthenticated,))
def get_chat_for_user(request, user_id):
    user = MyUser.objects.get(id=user_id)
    chat = ChatSession.objects.get_or_create_by_users(request.user, user)
    other_side = chat.get_interlocutor(request.user)
    if other_side.user_blocks.filter(blocked_user=request.user).exists():
        return Response({'detail': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ChatSessionDeatilSerializer(chat, context={'request': request})
    return Response(data=serializer.data)