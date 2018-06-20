# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-29 17:49
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0003_auto_20170526_1648'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lawsuit', '0003_auto_20170529_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True, verbose_name='Ativo')),
                (
                'legacy_code', models.CharField(default='', max_length=255, unique=True, verbose_name='Código Legado')),
                ('delegation_date',
                 models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data de Delegação')),
                ('acceptance_date', models.DateTimeField(null=True, verbose_name='Data de Aceitação')),
                ('first_deadline_date', models.DateTimeField(null=True, verbose_name='Primeiro Prazo')),
                ('second_deadline_date', models.DateTimeField(null=True, verbose_name='Segundo Prazo')),
                ('execution_date', models.DateTimeField(null=True, verbose_name='Data de Execução')),
                ('return_date', models.DateTimeField(null=True, verbose_name='Data de Retorno')),
                ('refused_date', models.DateTimeField(null=True, verbose_name='Data de Recusa')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                                 related_name='task_alter_user', to=settings.AUTH_USER_MODEL)),
                ('create_user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_create_user',
                                   to=settings.AUTH_USER_MODEL)),
                ('id_person_asked_by',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_asked_by',
                                   to='core.Person', verbose_name='Solicitante')),
                ('id_person_executed_by',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_executed_by',
                                   to='core.Person', verbose_name='Correspondente')),
                ('movement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lawsuit.Movement',
                                               verbose_name='Movimentação')),
                ('type_movement',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lawsuit.TypeMovement',
                                   verbose_name='Tipo de Movimentação')),
            ],
            options={
                'db_table': 'task',
                'verbose_name_plural': 'Providências',
                'verbose_name': 'Providência',
                'ordering': ['-id'],
            },
        ),
    ]
