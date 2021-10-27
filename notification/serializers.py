from rest_framework import serializers

from notification.models import FCMDevice, PushNotification


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        exclude = ('participant',)

    def create(self, validated_data):
        answer, created = FCMDevice.objects.update_or_create(
            participant=self.context['request'].user,
            defaults={'device': validated_data['device'],
                      'participant': self.context['request'].user})
        return answer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotification
        exclude = ('recipient',)