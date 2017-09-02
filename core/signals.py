from django.contrib.auth.models import User
from django.db import models

from core.models import Person


def create_person(instance, sender, **kwargs):
    if not Person.objects.filter(auth_user=instance).first():
        Person.objects.create(
            legal_name=instance.first_name + instance.last_name,
            name=instance.first_name + instance.last_name,
            is_lawyer=False,
            is_correspondent=False,
            is_court=False,
            legal_type='F',
            alter_user=instance,
            auth_user=instance,
            create_user=instance,
            is_active=True,
            is_customer=False,
            is_supplier=False,
        )


models.signals.post_save.connect(create_person, sender=User, dispatch_uid='create_person')
