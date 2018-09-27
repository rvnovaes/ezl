# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-05 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0046_populate_task_task_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_number',
            field=models.PositiveIntegerField(
                default=0, unique=True, verbose_name='Número da Providência'),
            preserve_default=False,
        ),
    ]
