from django.db.models.signals import post_save
from django.dispatch import receiver

from manager.models import Template, TemplateValue
from manager.utils import new_template_value_obj
from core.models import Office


@receiver(post_save, sender=Template)
def template_post_save(sender, instance, created, **kwargs):
    if created:
        create_list = []
        default_value = instance.parameters.get('{}_default'.format(instance.type.lower()), None)
        for office in Office.objects.all():
            create_list.append(new_template_value_obj(instance, office, default_value))
        TemplateValue.objects.bulk_create(create_list)
    else:
        templates_value = TemplateValue.objects.filter(
            template=instance
        ).exclude(
            value__template_key=instance.template_key,
            value__template_type=instance.type)
        for template_value in templates_value:
            template_value.value['template_key'] = instance.template_key
            template_value.value['template_type'] = instance.type
            template_value.save()
