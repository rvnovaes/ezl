# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-01 13:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0113_auto_20180925_1126'),
        ('lawsuit', '0050_auto_20180925_1126'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourtDistrictComplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('legacy_code', models.CharField(blank=True, max_length=255, null=True, verbose_name='Código legado')),
                ('system_prefix',
                 models.CharField(blank=True, choices=[('Advwin', 'Advwin'), ('Autojur', 'Autojur'), ('eLaw', 'Elaw')],
                                  max_length=255, null=True, verbose_name='Prefixo do sistema')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                                 related_name='courtdistrictcomplement_alter_user',
                                                 to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('court_district',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lawsuit.CourtDistrict',
                                   verbose_name='Comarca')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                  related_name='courtdistrictcomplement_create_user',
                                                  to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                             related_name='courtdistrictcomplement_office', to='core.Office',
                                             verbose_name='Escritório')),
            ],
            options={
                'verbose_name': 'Complemento de comarca',
                'verbose_name_plural': 'Complementos de comarca',
                'ordering': ('office', 'name'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='courtdistrictcomplement',
            unique_together=set([('name', 'court_district', 'office')]),
        ),
    ]
