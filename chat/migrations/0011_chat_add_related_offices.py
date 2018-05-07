# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-02-28 10:54
from __future__ import unicode_literals

from django.db import migrations


def chat_add_user_by_office(apps, schema_editor):
    from task.models import Task
    from task.signals import create_or_update_chat
    for task in Task.objects.all():
        create_or_update_chat(Task, task, False)

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0010_chat_offices'),
    ]

    operations = [
        migrations.RunPython(chat_add_user_by_office),
    ]
