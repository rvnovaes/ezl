# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-09 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecm', '0004_auto_20180208_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='object_id',
            field=models.IntegerField(db_index=True, verbose_name='ID do Registro'),
        ),
    ]
