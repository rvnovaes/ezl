# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-17 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0054_auto_20181016_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawsuit',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Observações'),
        ),
    ]
