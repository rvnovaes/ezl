# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-08 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0128_recreate_custom_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='office',
            name='cpf_cnpj',
            field=models.CharField(max_length=255, null=True, unique=True, verbose_name='CPF/CNPJ'),
        ),
    ]
