# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 17:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etl', '0003_auto_20171121_1729'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dashboardetl',
            options={'ordering': ('-execution_date_finish',), 'verbose_name': 'Dashboard ETL', 'verbose_name_plural': 'Dashboard ETL'},
        ),
    ]
