from django.contrib import admin

# Register your models here.
from chat.models import *

admin.site.register(Notification)
admin.site.register(ChatSession)
admin.site.register(Message)
