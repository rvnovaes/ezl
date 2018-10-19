# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-11 18:09
from __future__ import unicode_literals

from django.db import migrations, models
import task.models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0116_add_ecmtask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='final_deadline_date',
            field=models.DateTimeField(verbose_name='Prazo Fatal'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.CharField(choices=[('Solicitada', 'Requested'), ('Aceita pelo Service', 'Accepted_Service'), ('Em Aberto', 'Open'), ('A Cumprir', 'Accepted'), ('Cumprida', 'Done'), ('Retorno', 'Return'), ('Finalizada', 'Finished'), ('Recusada pelo Service', 'Refused_Service'), ('Recusada', 'Refused'), ('Glosada', 'Blockedpayment'), ('Inválida', 'Invalid'), ('Erro no sistema de origem', 'Error')], default=task.models.TaskStatus('Solicitada'), max_length=30, verbose_name='Status da OS'),
        ),
    ]
