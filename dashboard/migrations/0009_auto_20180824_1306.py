# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 16:06
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20180822_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "title": "string",\n    "subtitle": "string",\n    "value": "string",\n    "percent": "string",\n    "direction": "string"\n}', null=True, verbose_name='Schema'),
        ),
        migrations.AlterField(
            model_name='doughnutchart',
            name='schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "title": "string",\n    "labels": "list",\n    "values": "list"\n}', null=True, verbose_name='Schema'),
        ),
        migrations.AlterField(
            model_name='linechart',
            name='schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "labels": [\n        "PONTOS DA LINHA EX: [JANEIRO, FEVEREIRO, MARCO]"\n    ],\n    "datasets": [\n        {\n            "label": "LABEL DO INDICADOR EX: (AUDI\\u00caCIAS POR M\\u00caS)",\n            "data": [\n                "VALORES DO INDICADOR EX: 20, 47, 50"\n            ],\n            "backgroundColor": "COR DO BACKGROUND DE FUNDO CASO FILL = True, EX: blue",\n            "borderColor": "COR DA BORDA DA LINHA EX: blue",\n            "fill": false\n        }\n    ]\n}', null=True, verbose_name='Schema'),
        ),
    ]
