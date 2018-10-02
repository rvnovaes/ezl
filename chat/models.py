from django.db import models
from core.models import Audit, OfficeMixin, Office, Company
from django.contrib.auth.models import User

# Create your models here.


class Chat(Audit):
    company = models.ForeignKey(
        Company, related_name='company_chats', null=True, blank=True)
    offices = models.ManyToManyField(Office, related_name='chats')
    label = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    back_url = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-alter_date']

    def __str__(self):
        return self.label


class Message(Audit):
    chat = models.ForeignKey(Chat, related_name='messages')
    message = models.TextField(verbose_name='Mensagem')

    class Meta:
        ordering = ['create_date']

    def __str__(self):
        return self.message


class UserByChat(Audit):
    user_by_chat = models.ForeignKey(User, verbose_name='Usuario')
    chat = models.ForeignKey(Chat, verbose_name='chat', related_name='users')

    def __str__(self):
        return self.user_by_chat.username

    class Meta:
        indexes = [models.Index(fields=['user_by_chat_id'])]


class UnreadMessage(Audit):
    message = models.ForeignKey(Message)
    user_by_message = models.ForeignKey(UserByChat)

    def __str__(self):
        return self.user_by_message.user_by_chat.username

    class Meta:
        indexes = [models.Index(fields=['user_by_message_id'])]
