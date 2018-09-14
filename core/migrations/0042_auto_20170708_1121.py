# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-08 14:21
from __future__ import unicode_literals

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20170707_1532'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='is_client',
            new_name='is_customer',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='is_provider',
            new_name='is_supplier',
        ),
        migrations.AlterField(
            model_name='person',
            name='legal_name',
            field=models.CharField(
                max_length=255, verbose_name='Razão social/Nome completo'),
        ),
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(choices=[('F', 'Fisica'), ('J', 'Juridica')], default=core.models.LegalType(
                'J'), max_length=1, verbose_name='Tipo'),
        ),
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, default=models.CharField(
                max_length=255, verbose_name='Razão social/Nome completo'), max_length=255, null=True, verbose_name='Nome Fantasia/Apelido'),
        ),
    ]
