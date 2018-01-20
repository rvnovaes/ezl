# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-26 01:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_merge_20170625_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(choices=[('J', 'Jurídica'), ('F', 'Física')], max_length=1, verbose_name='Tipo'),
        ),
        migrations.AlterField(
            model_name='person',
            name='service_type',
            field=models.CharField(choices=[('N', 'Nao Aplicavel'), ('C', 'Cliente'), ('F', 'Fornecedor')], default='N', max_length=1, verbose_name='Tipo de Serviço'),
        ),
    ]
