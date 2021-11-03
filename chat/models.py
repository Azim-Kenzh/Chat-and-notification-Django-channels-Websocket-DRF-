from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
# from django.dispatch import receiver

from account.models import MyUser


UserModel = get_user_model()


class ChatSessionManager(models.Manager):
    def get_or_create_by_users(self, first_user, second_user):
        queryset = self.filter(Q(owner=first_user, other_side=second_user) |
                               Q(owner=second_user, other_side=first_user))
        instance = queryset.first()
        if not instance:
            instance = ChatSession.objects.create(owner=first_user, other_side=second_user)
        return instance


class ChatSession(models.Model):
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='отправитель', related_name='chats_owner')
    other_side = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='получатель', related_name='chats_other')
    objects = ChatSessionManager()

    # def str(self):
    #     return f"Chat with {self.other_side.username}"

    def get_interlocutor(self, user):
        other_side = self.other_side if user == self.owner else self.owner
        return other_side


class Message(models.Model):
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name='чат', related_name='messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(blank=True, null=True)
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='отправитель', related_name='messages')
    # read = models.BooleanField(default=False)


class Notification(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='notifications')
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name='чат', related_name='notifications')
    seen = models.BooleanField(default=False)

#
# @receiver(signals.post_save, sender=Notification)
# def pos_save_message(sender, instance, created, **kwargs):
#     from notification.tasks import send_new_message_notification
#
#     if created:
#         send_new_message_notification.delay(instance.id)


class ChatStatus(models.Model):
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name='чат', related_name='chatstatus')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='chatstatus')
    current = models.BooleanField(default=True)

    class Meta:
        unique_together = ('chat', 'user')

#
# @receiver(signals.post_save, sender=Message)
# def pos_save_message(sender, instance, created, **kwargs):
#     # from notification.tasks import send_new_message_notification
#
#     if created:
#         send_new_message_notification.delay(instance.id)
