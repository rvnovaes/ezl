from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver, Signal
from django.db.models.signals import post_init, pre_save, post_save, post_delete
from core.models import Person, Office
from core.permissions import create_permission
from guardian.shortcuts import get_groups_with_perms


def create_person(instance, sender, **kwargs):
    if not Person.objects.filter(auth_user=instance).first():
        Person.objects.create(
            legal_name=instance.first_name + ' ' + instance.last_name,
            name=instance.first_name + ' ' + instance.last_name,
            is_lawyer=False,
            legal_type='F',
            alter_user=instance,
            auth_user=instance,
            create_user=instance,
            is_active=True,
            is_customer=False,
            is_supplier=False,
            import_from_legacy=False,
            legacy_code=''
        )


models.signals.post_save.connect(create_person, sender=User, dispatch_uid='create_person')


@receiver(post_save, sender=Office)
def office_post_save(sender, instance, created, **kwargs):
    if created or not get_groups_with_perms(instance):
        create_permission(instance)
    else:
        for group in get_groups_with_perms(instance):
            group.name = '{}-{}-{}'.format(group.name.split('-')[0],
                                           instance.pk,
                                           instance.legal_name)
            group.save()


@receiver(post_delete, sender=Office)
def office_post_delete(sender, instance, **kwargs):
    for group in get_groups_with_perms(instance):
        group.delete()
