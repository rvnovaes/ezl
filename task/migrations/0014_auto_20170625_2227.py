# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-26 01:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0013_auto_20170622_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecm',
            name='task',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='task.Task'),
        ),
    ]
