# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-12 16:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0030_policy_price_default'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policyprice',
            options={'verbose_name': 'Tipos de preço'},
        ),
        migrations.RemoveField(
            model_name='policyprice',
            name='billing_type',
        ),
        migrations.AlterField(
            model_name='policyprice',
            name='billing_moment',
            field=models.CharField(choices=[('PRE_PAID', 'Pré-pago'), ('POST_PAID', 'Pós-pago')], max_length=255, verbose_name='Momento do faturamento'),
        ),
        migrations.AlterField(
            model_name='policyprice',
            name='category',
            field=models.CharField(choices=[('PREPAID', 'Pré-pago'), ('POSTPAID', 'Pós-pago'), ('PUBLIC', 'Público'), ('NETWORK', 'Rede')], max_length=255, verbose_name='Categoria'),
        ),
        migrations.AlterField(
            model_name='servicepricetable',
            name='policy_price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='service_prices', to='financial.PolicyPrice', verbose_name='Tipo de preço'),
        ),
    ]