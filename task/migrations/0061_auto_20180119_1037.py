# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-19 12:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0060_task_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='parent',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='task.Task'),
        ),
    ]
