# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-07 18:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20170706_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='legacy_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AddField(
            model_name='person',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
    ]
