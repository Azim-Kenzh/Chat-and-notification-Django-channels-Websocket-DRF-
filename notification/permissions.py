from rest_framework import permissions

from chat.models import ChatSession


class IsChatUser(permissions.BasePermission):
    ''' Only access only to chat user '''
    def has_object_permission(self, request, view, obj):
        chat = ChatSession.objects.get(id=self.kwargs.get('chat_id'))
        return request.user == chat.owner or request.user == chat.other_side