# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-26 18:15
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models.signals import post_save, pre_save
from task.signals import post_save_task, pre_save_task
import django.utils.timezone


def update_task_checkin_fields(apps, schema_editor):
    TaskGeolocation = apps.get_model('task', 'TaskGeolocation')
    Task = apps.get_model('task', 'Task')
    post_save.disconnect(post_save_task, sender=Task)
    pre_save.disconnect(pre_save_task, sender=Task)
    for taskgeolocation in TaskGeolocation.objects.all().order_by('id'):
        task = taskgeolocation.task
        task.executed_by_checkin = taskgeolocation
        task.save()
        while task.parent:
            task = task.parent
            task.executed_by_checkin = taskgeolocation
            task.save()
    post_save.connect(post_save_task, sender=Task)
    pre_save.connect(pre_save_task, sender=Task)


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0128_auto_20181212_1550'),
    ]

    operations = [
        migrations.RunPython(update_task_checkin_fields),
    ]
