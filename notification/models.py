# from django.contrib.auth import get_user_model
# from django.db import models
#
# User = get_user_model()
#
#
# class FCMDevice(models.Model):
#     participant = models.OneToOneField(User, related_name='device', on_delete=models.CASCADE)
#     device = models.TextField()
#
#     def str(self):
#         return f'{self.participant} device number'
#
#
# POST_LIKE = 'post_like'
# POST_COMMENT = 'post_comment'
# CHAT_MESSAGE = 'chat_message'
#
# NOTIFICATION_TYPES = (
#     (POST_LIKE, 'post like'),
#     (POST_COMMENT, 'post comment'),
#     (CHAT_MESSAGE, 'chat message'),
# )
#
#
# class PushNotification(models.Model):
#     recipient = models.ForeignKey(User, related_name='user_device_notifications', on_delete=models.CASCADE)
#     title = models.CharField(max_length=256, null=True, blank=True)
#     message = models.TextField()
#     read = models.BooleanField(default=False)
#     type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     object_id = models.CharField(max_length=50)  # uuid or id
#     image_url = models.URLField(blank=True)
#     post_image = models.URLField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def str(self):
#         return f'{self.title} {self.message}'