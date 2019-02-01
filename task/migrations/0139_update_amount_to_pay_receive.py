# -*- coding: utf-8 -*-
# Created by Tiago Gomes on 2019-02-01 10:00
from __future__ import unicode_literals
from django.db import migrations
from django.db.models import F


def update_task(apps, schema_editor):
    Task = apps.get_model('task', 'Task')
    Task.objects.update(amount_to_pay=F('amount'), amount_to_receive=F('amount'))


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0138_auto_20190201_1015'),
    ]

    operations = [
        migrations.RunPython(update_task),
    ]
