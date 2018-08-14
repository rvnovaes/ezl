# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-14 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_card_direction_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='direction_value',
        ),
        migrations.RemoveField(
            model_name='card',
            name='percent',
        ),
        migrations.RemoveField(
            model_name='card',
            name='subtitle',
        ),
        migrations.RemoveField(
            model_name='card',
            name='title',
        ),
        migrations.RemoveField(
            model_name='card',
            name='value',
        ),
        migrations.AddField(
            model_name='card',
            name='code',
            field=models.TextField(blank=True, null=True, verbose_name='Codigo'),
        ),
        migrations.AddField(
            model_name='card',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nome'),
        ),
    ]
