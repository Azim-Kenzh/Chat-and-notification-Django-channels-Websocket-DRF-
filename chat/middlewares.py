from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from account.models import MyUser


@database_sync_to_async
def get_user(token):
    try:
        return Token.objects.get(key=token.decode().split('=')[1]).user
    except MyUser.DoesNotExist:
        return AnonymousUser()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        scope['user'] = await get_user(scope["query_string"])
        # scope['user'] = await get_user(int(scope["token"]))

        return await self.app(scope, receive, send)
