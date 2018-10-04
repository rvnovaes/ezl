# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-09 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalapplication',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.Company',
                verbose_name='Empresa'),
        ),
    ]
