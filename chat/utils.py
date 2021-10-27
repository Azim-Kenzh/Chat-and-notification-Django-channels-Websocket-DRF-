import channels
from asgiref.sync import async_to_sync


def broadcast_to_groups(group_name, consumer_method, data):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(group_name,
                                            {'type': consumer_method,
                                             'data': data})