# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_auto_20180814_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.ImageField(
                blank=True, null=True, upload_to='', verbose_name='Logo'),
        ),
    ]