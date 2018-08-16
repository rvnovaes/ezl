# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-16 15:31
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0098_auto_20180816_1231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True,
                                          max_length=255, null=True, verbose_name='Nome')),
                ('code', models.TextField(blank=True,
                                          null=True, verbose_name='Codigo')),
                ('schema', django.contrib.postgres.fields.jsonb.JSONField(
                    blank=True, default='{"title": "string", "subtitle": "string", "value": "string", "percent": "string", "direction": "string"}', null=True, verbose_name='Schema')),
            ],
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh', models.IntegerField(blank=True,
                                                null=True, verbose_name='Refresh por millesegundo')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              to='core.Company', verbose_name='Empresa')),
            ],
        ),
        migrations.CreateModel(
            name='DashboardCard',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.ForeignKey(
                    blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Card')),
                ('dashboard', models.ForeignKey(
                    blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Dashboard')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='dashboards',
            field=models.ManyToManyField(
                blank=True, related_name='cards', through='dashboard.DashboardCard', to='dashboard.Dashboard'),
        ),
    ]
