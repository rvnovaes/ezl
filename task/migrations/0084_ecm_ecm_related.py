# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-12 13:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0083_ecm_exhibition_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecm',
            name='ecm_related',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='child',
                to='task.Ecm'),
        ),
    ]
