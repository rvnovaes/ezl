# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-23 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_merge_20170623_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='service_type',
            field=models.CharField(
                choices=[('N', 'Nao Aplicavel'), ('C', 'Cliente'),
                         ('F', 'Fornecedor')],
                default='N',
                max_length=1,
                verbose_name='Tipo de Serviço'),
        ),
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(
                choices=[('J', 'Jurídica'), ('F', 'Física')],
                max_length=1,
                verbose_name='Tipo'),
        ),
    ]
