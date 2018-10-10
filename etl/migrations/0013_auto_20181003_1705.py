# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-03 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etl', '0012_auto_20180105_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inconsistencyetl',
            name='inconsistency',
            field=models.CharField(blank=True, choices=[('OS sem movimentação', 'Tasklessmovement'), ('Movimentação sem processo', 'Movementlessprocess'), ('OS em Pasta Inativa', 'Taskinativefolder'), ('O valor preenchido no campo comarca não foi encontrado como Comarca, Cidade ou Complemento de comarca', 'Invalidcourtdistrict'), ('O campo comarca não foi preenchido', 'Blankcourtdistrict')], max_length=150, null=True, verbose_name='Inconsistência'),
        ),
    ]