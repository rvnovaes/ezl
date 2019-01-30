# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-10 19:43
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_fixture_20180918_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='BarChart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('code', models.TextField(blank=True, null=True, verbose_name='Codigo')),
                ('schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "title": "string",\n    "labels": "list",\n    "values": "list"\n}', null=True, verbose_name='Schema')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DashboardBarChart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(verbose_name='Sequencia')),
                ('bar_chart', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.BarChart')),
                ('dashboard', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Dashboard')),
            ],
            options={
                'ordering': ['sequence'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='barchart',
            name='dashboards',
            field=models.ManyToManyField(blank=True, related_name='bar_charts', through='dashboard.DashboardBarChart', to='dashboard.Dashboard'),
        ),
    ]