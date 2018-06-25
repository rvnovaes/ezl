# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-08 19:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0007_auto_20170607_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='law_suit_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lawsuit.LawSuitInstance', verbose_name='Instância do Processo'),
        ),
    ]
