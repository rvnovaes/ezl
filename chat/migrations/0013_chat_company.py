# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_auto_20180814_1737'),
        ('chat', '0012_auto_20180507_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='company_chats',
                to='core.Company'),
        ),
    ]
