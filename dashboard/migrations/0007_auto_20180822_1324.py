# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-22 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20180822_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='name',
            field=models.CharField(default='EM BRANCO', max_length=255, verbose_name='Nome'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doughnutchart',
            name='name',
            field=models.CharField(default='EM BRANCO', max_length=255, verbose_name='Nome'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='linechart',
            name='name',
            field=models.CharField(default='EM BRANCO', max_length=255, verbose_name='Nome'),
            preserve_default=False,
        ),
    ]
