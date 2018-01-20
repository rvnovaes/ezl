# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-13 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0009_courtdivision_typetask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courtdivision',
            name='legacy_code',
            field=models.CharField(max_length=255, unique=True, verbose_name='Código Legado'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='legacy_code',
            field=models.CharField(max_length=255, unique=True, verbose_name='Código Legado'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Tipo de Serviço'),
        ),
    ]
