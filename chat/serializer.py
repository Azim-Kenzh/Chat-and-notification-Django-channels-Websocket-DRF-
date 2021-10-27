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
from chat.models import Message, ChatSession


class MessageSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(auto_now_add=True)

    class Meta:
        model = Message
        fields = '__all__'


# class MessageImageSerializer(serializers.ModelSerializer):
#     image = serializers.ImageField(required=True)
#
#     class Meta:
#         model = Message
#         fields = ('image',)


class MessageFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Message
        fields = ('file',)


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id', 'other_side')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['other_side'] = MyUser(
            instance.get_interlocutor(self.context['request'].user),
            context={'request': self.context['request']}
        ).data
        representation['latest_message'] = MessageSerializer(
            instance.messages.latest('timestamp'),
            context={'request': self.context['request']}
        ).data if instance.messages.exists() else None
        representation['unread_count'] = instance.unread_count
        return representation


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
