# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-13 20:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='code',
            new_name='value',
        ),
    ]
