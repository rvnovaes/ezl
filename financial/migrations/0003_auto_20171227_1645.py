# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-27 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0002_servicepricetable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicepricetable',
            name='value',
            field=models.DecimalField(
                decimal_places=2, max_digits=9, verbose_name='Valor'),
        ),
    ]
