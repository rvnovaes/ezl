# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-03 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0054_auto_20171221_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='chat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.Chat', verbose_name='Chat'),
        ),
        migrations.AlterField(
            model_name='taskhistory',
            name='status',
            field=models.CharField(choices=[('A Cumprir', 'ACCEPTED'), ('Em Aberto', 'OPEN'), ('Retorno', 'RETURN'), ('Cumprida', 'DONE'), ('Recusada', 'REFUSED'), ('Glosada', 'BLOCKEDPAYMENT'), ('Finalizada', 'FINISHED'), ('Inválida', 'INVALID'), ('Erro no sistema de origem', 'ERROR')], max_length=30),
        ),
    ]
