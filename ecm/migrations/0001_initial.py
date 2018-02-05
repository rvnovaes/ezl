# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-25 16:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import ecm.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0066_office_import_from_legacy'),
        ('task', '0061_typetask_survey'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lawsuit', '0043_auto_20180105_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('legacy_code', models.CharField(blank=True, max_length=255, null=True, verbose_name='Código legado')),
                ('system_prefix', models.CharField(blank=True, choices=[('Advwin', 'Advwin')], max_length=255, null=True, verbose_name='Prefixo do sistema')),
                ('model_name', models.CharField(max_length=120, verbose_name='Model')),
                ('object_id', models.PositiveSmallIntegerField(db_index=True, verbose_name='ID do Registro')),
                ('file', models.FileField(upload_to=ecm.models.get_uploda_to, verbose_name='Arquivo')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attachment_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Anexo',
                'verbose_name_plural': 'Anexos',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='DefaultAttachmentRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='defaultattachmentrule_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.City', verbose_name='Cidade')),
                ('court_district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='lawsuit.CourtDistrict', verbose_name='Comarca')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='defaultattachmentrule_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='defaultattachmentrule_office', to='core.Office', verbose_name='Escritório')),
                ('person_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='defaultattachmentrule_customer', to='core.Person', verbose_name='Solicitante')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.State', verbose_name='Estado')),
                ('type_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='task.TypeTask', verbose_name='Tipo de Serviço')),
            ],
            options={
                'verbose_name': 'Regra de Anexo Padrão',
                'verbose_name_plural': 'Regras de Anexo Padrão',
                'ordering': ['-id'],
            },
        ),
    ]
