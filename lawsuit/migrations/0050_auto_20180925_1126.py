# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-25 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0049_auto_20180920_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courtdistrict',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='courtdivision',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='lawsuit',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
    ]
