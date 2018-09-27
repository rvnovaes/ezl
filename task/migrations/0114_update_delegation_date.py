# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-26 18:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import logging
logger = logging.getLogger('0114')


def update_delegation_date(apps, schema_editor):    
    from task.models import Task, TaskStatus   
    for task in Task.objects.filter(
        delegation_date__isnull=False, task_status__in=[TaskStatus.ERROR, TaskStatus.REQUESTED, TaskStatus.ACCEPTED_SERVICE]):
        task.delegation_date = None
        task.save(**{'skip_signal': True, 'skip_mail': True})
        logger.info('AJUSTADO delegation_date de OS - {} COM O STATUS {}'.format(str(task.task_number), str(task.status)))


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0113_auto_20180926_1515'),
    ]

    operations = [
        migrations.RunPython(update_delegation_date),    
    ]
