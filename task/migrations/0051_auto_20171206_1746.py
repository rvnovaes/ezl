# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-06 19:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import task.models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0050_auto_20171205_1548'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={
                'ordering': ['-alter_date'],
                'permissions': [('view_delegated_tasks',
                                 'Can view tasks delegated to the user'),
                                ('view_all_tasks', 'Can view all tasks'),
                                ('return_all_tasks', 'Can return tasks'),
                                ('validate_all_tasks', 'Can validade tasks'),
                                ('view_requested_tasks',
                                 'Can view tasks requested by the user'),
                                ('block_payment_tasks',
                                 'Can block tasks payment'),
                                ('can_access_general_data',
                                 'Can access general data screens'),
                                ('view_distributed_tasks',
                                 'Can view tasks distributed by the user'),
                                ('can_distribute_tasks',
                                 'Can distribute tasks to another user')],
                'verbose_name':
                'Providência',
                'verbose_name_plural':
                'Providências'
            },
        ),
        migrations.AlterField(
            model_name='task',
            name='amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=9,
                verbose_name='Valor'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.CharField(
                choices=[('Solicitada', 'Requested'),
                         ('Aceita pelo Service', 'Accepted_Service'),
                         ('Em Aberto', 'Open'), ('A Cumprir', 'Accepted'),
                         ('Cumprida', 'Done'), ('Retorno', 'Return'),
                         ('Finalizada', 'Finished'),
                         ('Recusada pelo Service', 'Refused_Service'),
                         ('Recusada', 'Refused'), ('Glosada',
                                                   'Blockedpayment'),
                         ('Inválida', 'Invalid')],
                default=task.models.TaskStatus('Em Aberto'),
                max_length=30,
                verbose_name=''),
        ),
        migrations.AlterField(
            model_name='taskhistory',
            name='status',
            field=models.CharField(
                choices=[('Solicitada', 'REQUESTED'),
                         ('Aceita pelo Service', 'ACCEPTED_SERVICE'),
                         ('Em Aberto', 'OPEN'), ('A Cumprir', 'ACCEPTED'),
                         ('Cumprida', 'DONE'), ('Retorno', 'RETURN'),
                         ('Finalizada', 'FINISHED'),
                         ('Recusada pelo Service', 'REFUSED_SERVICE'),
                         ('Recusada', 'REFUSED'), ('Glosada',
                                                   'BLOCKEDPAYMENT'),
                         ('Inválida', 'INVALID')],
                max_length=10),
        ),
        migrations.AlterField(
            model_name='task',
            name='person_distributed_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='core.Person',
                verbose_name='Contratante'),
        ),
    ]
