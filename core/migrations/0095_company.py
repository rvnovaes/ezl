# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-09 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0094_auto_20180808_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('name',
                 models.CharField(max_length=255, verbose_name='Empresa')),
            ],
        ),
    ]
