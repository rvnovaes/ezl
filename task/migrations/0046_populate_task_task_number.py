# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-05 13:04
from __future__ import unicode_literals

from django.db.models import F
from django.db import migrations

from sequences import get_next_value


def populate_task_task_number(apps, schema_editor):
    Task = apps.get_model('task', 'Task')
    tasks = Task.objects.order_by('id')
    if tasks.exists():
        print(tasks.update(task_number=F('id')))
        last_id = tasks.last().pk
        from task.models import Task
        assert last_id == get_next_value(Task.TASK_NUMBER_SEQUENCE, initial_value=last_id)


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0045_task_task_number'),
    ]

    operations = [
        migrations.RunPython(populate_task_task_number),
    ]
