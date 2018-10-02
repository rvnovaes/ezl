# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 18:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardETL',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('create_date',
                 models.DateTimeField(
                     auto_now_add=True, verbose_name='Criado em')),
                ('alter_date',
                 models.DateTimeField(
                     auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('execution_date_initial',
                 models.DateTimeField(auto_now=True, verbose_name='Inicio')),
                ('execution_date_finish',
                 models.DateTimeField(verbose_name='Fim')),
                ('name', models.CharField(max_length=100, verbose_name='ETL')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='dashboardetl_alter_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Alterado por')),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='dashboardetl_create_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Dashboard ETL',
                'verbose_name_plural': 'Dashboard ETL',
                'db_table': 'dashboard_etl',
                'ordering': ('execution_date_finish', ),
            },
        ),
    ]
