from django.contrib import admin
from chat.models import Chat, Message, UserByChat, UnreadMessage
# Register your models here.


class UnreadMessageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'message', 'user_by_message']

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(UserByChat)
admin.site.register(UnreadMessage, UnreadMessageAdmin)
