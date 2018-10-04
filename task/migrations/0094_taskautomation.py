# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-03 17:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import task.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task', '0093_auto_20180903_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskAutomation',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('create_date',
                 models.DateTimeField(
                     auto_now_add=True, verbose_name='Criado em')),
                ('alter_date',
                 models.DateTimeField(
                     auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('task_from',
                 models.CharField(
                     choices=[('Solicitada', 'Requested'),
                              ('Aceita pelo Service', 'Accepted_Service'),
                              ('Em Aberto', 'Open'), ('A Cumprir', 'Accepted'),
                              ('Cumprida', 'Done'), ('Retorno', 'Return'),
                              ('Finalizada', 'Finished'),
                              ('Recusada pelo Service', 'Refused_Service'),
                              ('Recusada', 'Refused'),
                              ('Glosada', 'Blockedpayment'),
                              ('Inválida', 'Invalid'),
                              ('Erro no sistema de origem', 'Error')],
                     default=task.models.TaskStatus('Solicitada'),
                     max_length=30,
                     verbose_name='')),
                ('task_to',
                 models.CharField(
                     choices=[('Solicitada', 'Requested'),
                              ('Aceita pelo Service', 'Accepted_Service'),
                              ('Em Aberto', 'Open'), ('A Cumprir', 'Accepted'),
                              ('Cumprida', 'Done'), ('Retorno', 'Return'),
                              ('Finalizada', 'Finished'),
                              ('Recusada pelo Service', 'Refused_Service'),
                              ('Recusada', 'Refused'),
                              ('Glosada', 'Blockedpayment'),
                              ('Inválida', 'Invalid'),
                              ('Erro no sistema de origem', 'Error')],
                     default=task.models.TaskStatus('Solicitada'),
                     max_length=30,
                     verbose_name='')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='taskautomation_alter_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Alterado por')),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='taskautomation_create_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Criado por')),
                ('responsible_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]