# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0101_company_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Logo'),
        ),
    ]
