# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-31 19:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20170530_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(
                choices=[('F', 'Física'), ('J', 'Jurídica')],
                max_length=1,
                verbose_name='Tipo'),
        ),
    ]
