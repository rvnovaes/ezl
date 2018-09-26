# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-09 15:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0044_auto_20180208_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawsuit',
            name='organ',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='organs', to='lawsuit.Organ', verbose_name='Órgão'),
        ),
    ]
