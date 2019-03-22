# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-07 20:42
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Count
import uuid
import logging
LOGGER = logging.getLogger('0143_fix_task_hash')


def fix_task_hash(apps, schema_editor):
    Task = apps.get_model('task', 'Task')
    duplicates_hash = Task.objects.values('task_hash').annotate(
        Count('task_hash')).order_by().filter(task_hash__count__gt=1)
    for item in duplicates_hash: 
        tasks = Task.objects.filter(task_hash=item.get('task_hash'))
        for task in tasks: 
            task.task_hash = uuid.uuid4()
            task.save()
            LOGGER.info('AJUSTADO task_hash da OS {} para {}'.format(task.task_number, task.task_hash))

class Migration(migrations.Migration):

    dependencies = [
        ('task', '0142_auto_20190215_1254'),
    ]

    operations = [
        migrations.RunPython(fix_task_hash),
    ]