# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-08 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_auto_20180208_1532'),
        ('lawsuit', '0043_auto_20180105_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courtdivision',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Vara'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Nome'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Nome'),
        ),
        migrations.AlterUniqueTogether(
            name='courtdivision',
            unique_together=set([('name', 'office')]),
        ),
        migrations.AlterUniqueTogether(
            name='folder',
            unique_together=set([('folder_number', 'person_customer', 'office')]),
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([('name', 'office')]),
        ),
        migrations.AlterUniqueTogether(
            name='lawsuit',
            unique_together=set([('instance', 'law_suit_number', 'office')]),
        ),
        migrations.AlterUniqueTogether(
            name='typemovement',
            unique_together=set([('name', 'office')]),
        ),
    ]
