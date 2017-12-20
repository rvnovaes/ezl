from django.db import models
from core.models import Audit


# Create your models here.
class Chat(Audit):
    label = models.SlugField(unique=True)


class Message(Audit):
    chat = models.ForeignKey(Chat, related_name='messages')
    message = models.TextField(verbose_name='Mensagem')
