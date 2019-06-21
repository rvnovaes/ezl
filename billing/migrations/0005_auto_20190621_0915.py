# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-21 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_billingdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingdetails',
            name='cpf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='CPF'),
        ),
        migrations.AddField(
            model_name='billingdetails',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nome completo'),
        ),
    ]
