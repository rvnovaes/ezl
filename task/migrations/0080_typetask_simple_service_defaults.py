# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-05-14 17:08
from __future__ import unicode_literals
from django.db import migrations
from django.core.management import call_command

fixture = 'type_task'


def load_fixture(apps, schema_editor):
    from django.contrib.auth.models import User

    user = User.objects.filter(username='admin').first()
    if not user:
        return True
    call_command('loaddata', fixture, app_label='task')


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0079_typetask_simple_service'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
