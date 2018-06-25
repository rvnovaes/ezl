# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 17:59
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('lawsuit', '0004_auto_20170530_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='law_suit_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lawsuit.LawSuitInstance',
                                    verbose_name='Instância do Processo'),
        ),
    ]
