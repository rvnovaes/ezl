# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-21 16:24
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0132_companyuser_show_administrative_menus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('template_key', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Chave')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('type', models.CharField(choices=[('BOOLEAN', 'Boleano'), ('FOREIGN_KEY', 'Chave estrangeira'), ('DECIMAL', 'Decimal'), ('INTEGER', 'Inteiro'), ('LONG_TEXT', 'Texto Longo'), ('SIMPLE_TEXT', 'Texto Simples')], max_length=15, verbose_name='Tipo')),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Características disponíveis')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='template_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='template_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Template de configuração',
                'verbose_name_plural': 'Templates de configuração',
                'ordering': ('name', 'type'),
            },
        ),
        migrations.CreateModel(
            name='TemplateValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('value', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{\n    "office_id": null,\n    "template_key": null,\n    "value": null\n}', null=True, verbose_name='Valor')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templatevalue_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='templatevalue_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='templatevalue_office', to='core.Office', verbose_name='Escritório')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.Template', verbose_name='Configuração')),
            ],
            options={
                'verbose_name': 'Configuração por escritório',
                'verbose_name_plural': 'Configurações por escritório',
                'ordering': ('office', 'template'),
            },
        ),
    ]
