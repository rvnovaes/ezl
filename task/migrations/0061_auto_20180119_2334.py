# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-20 01:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0060_auto_20180119_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filter',
            name='auth_user',
        ),
        migrations.AlterField(
            model_name='filter',
            name='query',
            field=models.BinaryField(blank=True, null=True, verbose_name='query'),
        ),
    ]
