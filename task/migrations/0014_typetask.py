# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-23 14:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task', '0013_auto_20170622_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeTask',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('legacy_code',
                 models.CharField(
                     default='',
                     max_length=255,
                     unique=True,
                     verbose_name='Código legado')),
                ('system_prefix',
                 models.CharField(
                     choices=[('ADVWIN', '0')],
                     default='',
                     max_length=255,
                     verbose_name='Prefixo do Sistema')),
                ('name',
                 models.CharField(
                     max_length=255,
                     unique=True,
                     verbose_name='Tipo de Serviço')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='typetask_alter_user',
                     to=settings.AUTH_USER_MODEL)),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='typetask_create_user',
                     to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'type_task',
                'verbose_name': 'Tipo de Serviço',
                'verbose_name_plural': 'Tipos de Serviço',
            },
        ),
    ]
