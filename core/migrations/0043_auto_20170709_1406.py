# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-09 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20170708_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='cpf_cnpj',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='CPF/CNPJ'),
        ),
    ]
