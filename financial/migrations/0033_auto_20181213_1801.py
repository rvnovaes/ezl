# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-13 20:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0032_auto_20181213_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policyprice',
            options={'ordering': ['name'], 'verbose_name': 'Tipo de Preço', 'verbose_name_plural': 'Tipos de Preço'},
        ),
    ]
