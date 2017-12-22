from django.db import models
from core.models import Audit
from django.contrib.auth.models import User


# Create your models here.
class Chat(Audit):
    label = models.SlugField(unique=True)


class Message(Audit):
    chat = models.ForeignKey(Chat, related_name='messages')
    message = models.TextField(verbose_name='Mensagem')

    class Meta:
        ordering = ['create_date']


class UserByChat(Audit):
    user_by_chat = models.ForeignKey(User, verbose_name='Usuario')
    chat = models.ForeignKey(Chat, verbose_name='chat', related_name='users')




