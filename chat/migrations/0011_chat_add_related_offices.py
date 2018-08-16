# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-02-28 10:54
from __future__ import unicode_literals

from django.db import migrations


def chat_add_user_by_office(apps, schema_editor):
    from task.models import Task
    from chat.models import Message
    from task.signals import create_or_update_chat
    from django.db.models import Q
    last_tasks_to_update = list(set(map(lambda i: Task.objects.filter(chat=i.chat).first().pk, Message.objects.all().order_by('-create_date'))))

    if last_tasks_to_update:
        for task in Task.objects.filter(~Q(chat__pk__in=last_tasks_to_update)):
            create_or_update_chat(Task, task, False)

        # Nessario para manter o chat ordenado pelas ultimas mensagens
        for task_id in last_tasks_to_update:
            task = Task.objects.get(pk=task_id)
            create_or_update_chat(Task, task, False)

class Migration(migrations.Migration):
    dependencies = [
        ('task', '0079_typetask_simple_service'),
        ('core', '0079_office_public_office'),
        ('chat', '0010_chat_offices'),
    ]

    operations = [
        migrations.RunPython(chat_add_user_by_office),
    ]
