import json
from django.db.models.signals import post_save
from django.dispatch import receiver

from manager.models import Template, TemplateValue
from core.models import Office


@receiver(post_save, sender=Template)
def template_post_save(sender, instance, created, **kwargs):
    if created:
        create_list = []
        for office in Office.objects.all():
            value = {
                'office_id': office.id,
                'template_key': instance.template_key,
                'template_type': instance.type,
                'value': None,
            }
            create_list.append(TemplateValue(office=office,
                                             template=instance,
                                             create_user=instance.create_user,
                                             value=value))
        TemplateValue.objects.bulk_create(create_list)
