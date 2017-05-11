# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-11 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='typemovement',
            name='legacy_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='uses_wo',
            field=models.NullBooleanField(default=True),
        ),
    ]
