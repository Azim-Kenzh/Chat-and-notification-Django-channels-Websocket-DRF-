from rest_framework import generics, permissions, mixins, viewsets
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response

# from notification.permissions import IsRecipient
from notification.serializers import DeviceSerializer, \
    NotificationSerializer
# from apps.core.utils import CustomJsonRenderer
from notification.models import FCMDevice, PushNotification
from chat.models import Message


class UserDeviceView(generics.CreateAPIView):
    queryset = FCMDevice.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # renderer_classes = (CustomJsonRenderer,)


class PushNotificationView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    queryset = PushNotification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated)
    # renderer_classes = (CustomJsonRenderer,)

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user).order_by('-pk')

    @action(detail=False)
    def count(self, request, *args, **kwargs):
        unread_notifications_count = PushNotification.objects.filter(
            read=False, recipient=request.user
        ).count()
        unread_messages_count = Message.objects.filter(
            Q(chat__owner=request.user) |
            Q(chat__other_side=request.user)
        ).filter(read=False).exclude(sender=request.user).count()
        return Response(data={'unread_notifications_count': unread_notifications_count,
                              'unread_messages_count': unread_messages_count})