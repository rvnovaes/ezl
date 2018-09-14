# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-05 14:07
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'type_task_main', app_label='task')


def create_default_type_tasks(apps, schema_editor):
    from core.models import Office
    from task.utils import create_default_type_tasks
    offices = Office.objects.filter(typetask_office__isnull=True)
    for office in offices:
        create_default_type_tasks(office)


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0091_typetask_office'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeTaskMain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_hearing', models.BooleanField(default=False, verbose_name='É audiência')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Tipo de Serviço')),
                ('characteristics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "options": [\n        {\n            "name": "acting_area",\n            "title": "\\u00c1rea de atua\\u00e7\\u00e3o",\n            "options": [\n                "C\\u00edvel",\n                "Criminal",\n                "Trabalhista"\n            ]\n        },\n        {\n            "name": "participants",\n            "title": "Participantes",\n            "options": [\n                "Advogado",\n                "Preposto"\n            ]\n        }\n    ],\n    "criticality": [\n        {\n            "name": "minimal_period",\n            "title": "Prazo M\\u00ednimo (h)",\n            "value": 48\n        },\n        {\n            "name": "urgent_period",\n            "title": "Prazo de urg\\u00eancia (h)",\n            "value": 72\n        }\n    ]\n}', null=True, verbose_name='Características disponíveis')),
            ],
            options={
                'verbose_name': 'Tipo de Serviço Principal',
                'verbose_name_plural': 'Tipos de Serviço Principais',
                'ordering': ('name',),
            },
        ),
        migrations.RunPython(load_fixture),
        migrations.RemoveField(
            model_name='typetask',
            name='simple_service',
        ),
        migrations.RemoveField(
            model_name='typetask',
            name='is_audience',
        ),
        migrations.AlterField(
            model_name='typetask',
            name='survey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Survey', verbose_name='Tipo de Formulário'),
        ),
        migrations.AddField(
            model_name='typetask',
            name='type_task_main',
            field=models.ManyToManyField(related_name='type_tasks', to='task.TypeTaskMain', verbose_name='Tipo de Serviço Principal')
        ),
        migrations.RunPython(create_default_type_tasks),
    ]
