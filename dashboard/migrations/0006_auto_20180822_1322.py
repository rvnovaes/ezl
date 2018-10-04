# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-22 16:22
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20180820_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardLineChart',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('sequence', models.IntegerField(verbose_name='Sequencia')),
                ('dashboard',
                 models.ForeignKey(
                     blank=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to='dashboard.Dashboard')),
            ],
            options={
                'ordering': ['sequence'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LineChart',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('name',
                 models.CharField(
                     blank=True,
                     max_length=255,
                     null=True,
                     verbose_name='Nome')),
                ('code',
                 models.TextField(
                     blank=True, null=True, verbose_name='Codigo')),
                ('schema',
                 django.contrib.postgres.fields.jsonb.JSONField(
                     blank=True,
                     default='{}',
                     null=True,
                     verbose_name='Schema')),
                ('dashboards',
                 models.ManyToManyField(
                     blank=True,
                     related_name='line_charts',
                     through='dashboard.DashboardLineChart',
                     to='dashboard.Dashboard')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='doughnutchart',
            name='schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=
                '{"title": "string", "labels": "list", "values": "list"}',
                null=True,
                verbose_name='Schema'),
        ),
        migrations.AddField(
            model_name='dashboardlinechart',
            name='line',
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='dashboard.LineChart'),
        ),
    ]