# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-02 13:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0003_auto_20171227_1645'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicepricetable',
            options={
                'ordering': ['value'],
                'verbose_name': 'Tabela de preço de serviços',
                'verbose_name_plural': 'Tabelas de preço de serviços'
            },
        ),
    ]
