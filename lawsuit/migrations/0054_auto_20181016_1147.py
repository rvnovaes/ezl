# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-16 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0053_auto_20181002_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='typemovement',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Nome'),
        ),
    ]
