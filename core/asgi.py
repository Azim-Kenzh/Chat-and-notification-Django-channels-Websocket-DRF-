# mysite/asgi.py
import os

import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing
from chat.middlewares import QueryAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": QueryAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
