# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-21 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20170621_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(
                choices=[('J', 'Jurídica'), ('F', 'Física')],
                max_length=1,
                verbose_name='Tipo'),
        ),
    ]
