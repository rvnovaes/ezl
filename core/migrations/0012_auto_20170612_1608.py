# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20170612_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(
                choices=[('J', 'Jurídica'), ('F', 'Física')], max_length=1, verbose_name='Tipo'),
        ),
    ]
