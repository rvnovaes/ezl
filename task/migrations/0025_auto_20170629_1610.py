# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-29 19:10
from __future__ import unicode_literals

from django.db import migrations, models
import task.models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0024_merge_20170629_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.CharField(choices=[('A Cumprir', 'Accepted'), ('Em Aberto', 'Open'), ('Retorno', 'Return'), ('Cumprida', 'Done'), ('Recusada', 'Refused')], default=task.models.TaskStatus('Em Aberto'), max_length=30, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True, verbose_name='Prefixo do Sistema'),
        ),
    ]
