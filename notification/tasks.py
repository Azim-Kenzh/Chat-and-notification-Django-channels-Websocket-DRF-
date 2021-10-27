from celery import shared_task
from django.conf import settings
from pyfcm import FCMNotification

from notification.models import PushNotification, POST_COMMENT, \
    CHAT_MESSAGE, POST_LIKE
# from notification.utils import build_absolute_uri


# @shared_task
# def send_new_comment_notification(comment_id):
    # from apps.post.models import Comment

    # try:
    #     comment = Comment.objects.get(id=comment_id)
    # except Comment.DoesNotExist:
    #     raise Exception("Comment with given id does not exists.")
    # recipient = comment.post.author
    # if recipient != comment.author:
    #     username = comment.author.get_full_name_or_username()
    #     message = f'{username} commented on your post: "{comment.text}"'
    #     image_url = comment.author.photo.url if comment.author.photo else ''
    #
    #     notification = PushNotification.objects.create(recipient=recipient,
    #                                                    title="New comment",
    #                                                    message=message,
    #                                                    type=POST_COMMENT,
    #                                                    object_id=str(comment.post.id),
    #                                                    image_url=build_absolute_uri(image_url),
    #                                                    post_image=build_absolute_uri(comment.post.get_post_thumbnail()))
    #     data_payload = {
    #         'type': notification.type,
    #         'object_id': notification.object_id,
    #         'image_url': notification.image_url,
    #         'post_image': notification.post_image,
    #         'id': notification.id
    #     }
    #     send_notification(recipient, data_payload, notification.title, notification.message)


@shared_task
def send_new_message_notification(message_id):
    from chat.models import Message

    try:
        chat_message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        raise Exception("Message with given id does not exists.")
    recipient = chat_message.chat.get_interlocutor(chat_message.sender)
    username = chat_message.sender.get_full_name_or_username()
    if chat_message.sender != recipient:
        if chat_message.text:
            message = f'{username}: "{chat_message.text}"'
        elif chat_message.image:
            message = f'{username} sent you new image'
        else:
            message = f'{username} sent you new file'
        image_url = chat_message.sender.photo.url if chat_message.sender.photo else ''
        notification = PushNotification.objects.create(recipient=recipient,
                                                       title="New message",
                                                       message=message,
                                                       type=CHAT_MESSAGE,
                                                       object_id=str(chat_message.sender.id))
                                                       # image_url=build_absolute_uri(image_url))
        data_payload = {
            'type': notification.type,
            'object_id': notification.object_id,
            'image_url': notification.image_url,
            'id': notification.id
        }
        send_notification(recipient, data_payload, notification.title, notification.message)
#
#
# @shared_task
# def send_new_like_notification(post_id, user_id):
#     from apps.post.models import Post
#     from apps.authentication.models import Profile
#
#     try:
#         post = Post.objects.get(id=post_id)
#         user = Profile.objects.get(id=user_id)
#     except (Post.DoesNotExist, Profile.DoesNotExist):
#         raise Exception("Post or Profile with given id does not exists.")
#
# recipient = post.author
#     if user != recipient:
#         message = f'{user.get_full_name_or_username()} liked your post'
#         image_url = user.photo.url if user.photo else ''
#         notification = PushNotification.objects.create(recipient=recipient,
#                                                        title="New notification",
#                                                        message=message,
#                                                        type=POST_LIKE,
#                                                        object_id=str(post.id),
#                                                        image_url=build_absolute_uri(image_url),
#                                                        post_image=build_absolute_uri(post.get_post_thumbnail()))
#         data_payload = {
#             'type': notification.type,
#             'object_id': notification.object_id,
#             'image_url': notification.image_url,
#             'post_image': notification.post_image,
#             'id': notification.id
#         }
#         send_notification(recipient, data_payload, notification.title, notification.message)


def send_notification(recipient, data_payload, title, body):
    fcm = FCMNotification(api_key=settings.FIREBASE_API_KEY)
    try:
        if hasattr(recipient, 'device'):
            return fcm.notify_single_device(
                registration_id=recipient.device.device,
                message_title=title,
                message_body=body,
                badge=recipient.user_device_notifications.filter(read=False).count(),
                data_message=data_payload,
                sound=True
            )
    except:
        pass