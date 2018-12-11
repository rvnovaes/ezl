# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-26 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0121_officenetwork'),
        ('financial', '0023_servicepricetable_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicepricetable',
            name='office_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='office_network', to='core.OfficeNetwork', verbose_name='Rede de escritórios'),
        ),
    ]
