# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-01 12:15
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0137_task_price_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='amount_to_pay',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=9, verbose_name='Valor a pagar'),
        ),
        migrations.AddField(
            model_name='task',
            name='amount_to_receive',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=9, verbose_name='Valor a receber'),
        ),
    ]
