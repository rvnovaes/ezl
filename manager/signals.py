from django.db.models.signals import post_save
from django.dispatch import receiver

from manager.models import Template, TemplateValue
from core.models import Office


@receiver(post_save, sender=Template)
def template_post_save(sender, instance, created, **kwargs):
    if created:
        create_list = []
        for office in Office.objects.all():
            create_list.append(TemplateValue(office=office,
                                             template=instance,
                                             create_user=instance.create_user))
        TemplateValue.objects.bulk_create(create_list)
