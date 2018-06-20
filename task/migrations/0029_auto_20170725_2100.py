# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-26 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0028_auto_20170706_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecm',
            name='legacy_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AddField(
            model_name='ecm',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
    ]
