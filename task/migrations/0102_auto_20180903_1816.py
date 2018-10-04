# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-03 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0101_auto_20180903_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasksettings',
            name='name',
            field=models.CharField(
                max_length=255, verbose_name='Nome da configuração'),
        ),
        migrations.AlterField(
            model_name='taskshowstatus',
            name='task_settings',
            field=models.ManyToManyField(
                related_name='status', to='task.TaskSettings'),
        ),
        migrations.AlterField(
            model_name='taskworkflow',
            name='task_settings',
            field=models.ManyToManyField(
                related_name='workflows', to='task.TaskSettings'),
        ),
    ]