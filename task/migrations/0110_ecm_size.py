# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-08-16 19:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0109_auto_20180917_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecm',
            name='size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]