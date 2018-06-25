# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-28 18:20
from __future__ import unicode_literals

from django.db import migrations, models

import task.models


class Migration(migrations.Migration):
    dependencies = [
        ('task', '0030_typetask_survey_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='survey_result',
            field=models.TextField(blank=True, null=True, verbose_name='Respotas do Formulário'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.CharField(
                choices=[('A Cumprir', 'Accepted'), ('Em Aberto', 'Open'), ('Retorno', 'Return'), ('Cumprida', 'Done'),
                         ('Recusada', 'Refused'), ('Glosada', 'Refusedpayment'), ('Válida', 'Validated'),
                         ('Inválida', 'Invalid')], default=task.models.TaskStatus('Em Aberto'), max_length=30,
                verbose_name=''),
        ),
        migrations.AlterField(
            model_name='taskhistory',
            name='status',
            field=models.CharField(
                choices=[('A Cumprir', 'ACCEPTED'), ('Em Aberto', 'OPEN'), ('Retorno', 'RETURN'), ('Cumprida', 'DONE'),
                         ('Recusada', 'REFUSED'), ('Glosada', 'BLOCKEDPAYMENT'), ('Válida', 'FINISHED'),
                         ('Inválida', 'INVALID')], max_length=10),
        ),
    ]
