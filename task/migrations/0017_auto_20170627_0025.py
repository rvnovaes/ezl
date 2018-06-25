# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('task', '0016_auto_20170626_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='task',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
    ]
