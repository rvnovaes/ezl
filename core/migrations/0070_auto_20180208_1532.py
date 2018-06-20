# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-08 17:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_auto_20180206_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Office'),
        ),
    ]
