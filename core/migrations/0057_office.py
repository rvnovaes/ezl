# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-05 19:25
from __future__ import unicode_literals

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0056_auto_20180112_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Office',
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
                ('legacy_code',
                 models.CharField(
                     blank=True,
                     max_length=255,
                     null=True,
                     verbose_name='Código legado')),
                ('system_prefix',
                 models.CharField(
                     blank=True,
                     choices=[('Advwin', 'Advwin')],
                     max_length=255,
                     null=True,
                     verbose_name='Prefixo do sistema')),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('legal_name',
                 models.CharField(
                     max_length=255,
                     verbose_name='Razão social/Nome completo')),
                ('name',
                 models.CharField(
                     blank=True,
                     max_length=255,
                     null=True,
                     verbose_name='Nome Fantasia/Apelido')),
                ('is_lawyer',
                 models.BooleanField(
                     default=False, verbose_name='É Advogado?')),
                ('legal_type',
                 models.CharField(
                     choices=[('F', 'Física'), ('J', 'Jurídica')],
                     default=core.models.LegalType('J'),
                     max_length=1,
                     verbose_name='Tipo')),
                ('cpf_cnpj',
                 models.CharField(
                     blank=True,
                     max_length=255,
                     null=True,
                     unique=True,
                     verbose_name='CPF/CNPJ')),
                ('is_customer',
                 models.BooleanField(default=False,
                                     verbose_name='É Cliente?')),
                ('is_supplier',
                 models.BooleanField(
                     default=False, verbose_name='É Fornecedor?')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='office_alter_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Alterado por')),
                ('auth_user',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Usuário do sistema')),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='office_create_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Criado por')),
                ('offices',
                 models.ManyToManyField(
                     blank=True,
                     related_name='_office_offices_+',
                     to='core.Office')),
                ('persons',
                 models.ManyToManyField(
                     blank=True, related_name='offices', to='core.Person')),
            ],
            options={
                'verbose_name': 'Escritório',
            },
        ),
    ]
