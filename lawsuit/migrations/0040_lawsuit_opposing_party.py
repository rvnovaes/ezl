# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 18:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0039_folder_cost_center'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawsuit',
            name='opposing_party',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Parte adversa'),
        ),
    ]
