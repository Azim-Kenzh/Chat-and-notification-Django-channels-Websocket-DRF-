# from rest_framework import serializers
#
# from chat.models import *
# from account.models import MyUser
#
#
# class ChatUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MyUser
#         fields = ('id', 'image', 'last_name', 'first_name')
#
#
# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = '__all__'
#
#
# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'


from rest_framework import serializers

from account.models import MyUser
from chat.models import Message, ChatSession, Notification


class ImageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('image', )


class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d.%m.%Y  %H:%M', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['first_name'] = instance.sender.first_name
        return representation


class UpdateNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('seen', )


class MessageFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Message
        fields = ('file',)


class ChatUserSerializer(serializers.ModelSerializer):
    has_unread = serializers.BooleanField(default=False)
    chat_exists = serializers.BooleanField(default=False)

    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name', 'chat_exists', 'has_unread')

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['owner'] = instance.owner.first_name and instance.owner.last_name
    #     return representation


    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['other_side'] = MyUser(
    #         instance.get_interlocutor(self.context.get('request')),
    #         context={'request': self.context.get('request')}
    #     ).data
    #     return representation


class ChatSessionDeatilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id', 'other_side')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['other_side'] = MyUser(
            instance.get_interlocutor(self.context['request'].user),
            context={'request': self.context['request']}
        ).data
        return representation
