from django.db.models.signals import post_init, pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver, Signal
from django.conf import settings
from chat.models import Chat, UserByChat, Message
from chat.utils import create_users_company_by_chat



@receiver(post_save, sender=Chat)
def pre_save_chat(sender, instance, created, **kwargs):    
    create_users_company_by_chat(instance.company, instance)