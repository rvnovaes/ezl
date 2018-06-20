# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('lawsuit', '0017_merge_20170626_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courtdivision',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='courtdivision',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
        migrations.AlterField(
            model_name='lawsuitinstance',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='lawsuitinstance',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='legacy_code',
            field=models.CharField(max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='system_prefix',
            field=models.CharField(choices=[('ADVWIN', '0')], max_length=255, null=True, unique=True,
                                   verbose_name='Prefixo do Sistema'),
        ),
    ]
