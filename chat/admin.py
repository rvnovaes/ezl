from django.contrib import admin
from chat.models import Chat, Message, UserByChat, UnreadMessage
# Register your models here.

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(UserByChat)
admin.site.register(UnreadMessage)
