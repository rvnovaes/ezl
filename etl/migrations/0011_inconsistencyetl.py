# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 12:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0053_auto_20171221_1002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('etl', '0010_auto_20171127_1658'),
    ]

    operations = [
        migrations.CreateModel(
            name='InconsistencyETL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('inconsistency', models.CharField(blank=True, choices=[('OS sem movimentação', 'Tasklessmovement'), ('Movimentação sem processo', 'Movementlessprocess'), ('OS em Pasta Inativa', 'Taskinativefolder')], max_length=50, null=True, verbose_name='Inconsistência')),
                ('solution', models.CharField(blank=True, max_length=100, null=True, verbose_name='Solução')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inconsistencyetl_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inconsistencyetl_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='task.Task', verbose_name='Providência')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
