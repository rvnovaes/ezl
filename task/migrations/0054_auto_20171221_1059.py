# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0053_auto_20171221_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskhistory',
            name='status',
            field=models.CharField(choices=[('A Cumprir', 'ACCEPTED'), ('Em Aberto', 'OPEN'), ('Retorno', 'RETURN'), ('Cumprida', 'DONE'), ('Recusada', 'REFUSED'), ('Glosada', 'BLOCKEDPAYMENT'), ('Finalizada', 'FINISHED'), ('Inválida', 'INVALID'), ('Erro no sistema de origem', 'ERROR')], max_length=30),
        ),
    ]
