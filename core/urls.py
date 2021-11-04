"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from chat.views import *

router = DefaultRouter()
router.register('chats/users', ChatUsersViewSet)
router.register('chats/messages', ChatMessagesViewSet)
router.register('chats/notification', UpdateNotificationViewSet)
# router.register('chats/users', ChatUserViewSet)
# router.register('chats/message', MessageViewSet)
# router.register('chats/notification', NotificationViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title='Stack API',
        default_version='v1',
        description='Test description',
    ),
    public=True,
)


urlpatterns = [
    path('docs/', schema_view.with_ui()),
    path('admin/', admin.site.urls),
    path('chats/', include('chat.urls')),
    path('accounts/', include('account.urls')),
    path('', include(router.urls)),
]

