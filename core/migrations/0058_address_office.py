# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-08 15:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_office'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Office'),
        ),
    ]
