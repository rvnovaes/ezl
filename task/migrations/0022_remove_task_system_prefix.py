# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 03:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('task', '0021_auto_20170627_0043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='system_prefix',
        ),
    ]
