# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-23 16:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0061_auto_20180119_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='person_executed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='task_executed_by', to='core.Person', verbose_name='Correspondente'),
        ),
    ]
