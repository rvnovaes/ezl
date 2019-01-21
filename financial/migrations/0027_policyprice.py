# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-12 13:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0121_officenetwork'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('financial', '0026_auto_20181226_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('category', models.CharField(choices=[('Padrão', 'DEFAULT'), ('Pública', 'PUBLIC'), ('Rede', 'NETWORK')], max_length=255, verbose_name='Categoria')),
                ('billing_type', models.CharField(choices=[('Avulso', 'PER_UNIT'), ('Mensal', 'PER_MONTH')], max_length=255, verbose_name='Tipo de faturamento')),
                ('billing_moment', models.CharField(choices=[('Pré-pago', 'PRE_PAID'), ('Pós-pago', 'POST_PAID')], max_length=255, verbose_name='Momento do faturamento')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='policyprice_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='policyprice_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='policyprice_office', to='core.Office', verbose_name='Escritório')),
            ],
            options={
                'verbose_name': 'Política de preço',
            },
        ),
    ]
