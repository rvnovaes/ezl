# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-12 13:19
from __future__ import unicode_literals
from django.db import migrations, models
import logging
logger = logging.getLogger('0032_service_price_table_policy_price')


def update_service_price_table(apps, schema_editor):
    from financial.models import CategoryPrice, BillingMoment
    PolicyPrice = apps.get_model('financial', 'PolicyPrice')
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    for service_price in ServicePriceTable.objects.all():
        if service_price.office == service_price.office_correspondent:
            service_price.policy_price = PolicyPrice.objects.filter(office=service_price.office,
                                                                    category=CategoryPrice.PUBLIC,
                                                                    billing_moment=BillingMoment.PRE_PAID).first()
        elif service_price.office_network:
            service_price.policy_price = PolicyPrice.objects.filter(office=service_price.office,
                                                                    category=CategoryPrice.NETWORK,
                                                                    billing_moment=BillingMoment.POST_PAID).first()
        else:
            service_price.policy_price = PolicyPrice.objects.filter(office=service_price.office,
                                                                    category=CategoryPrice.DEFAULT,
                                                                    billing_moment=BillingMoment.POST_PAID).first()
        service_price.save()        
        logging.info('ALTERADO TIPO DE PRECO NA TABLEA DE PRECOS: ID-{}'.format(service_price.pk))


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0031_auto_20181212_1416'),
    ]

    operations = [
        migrations.RunPython(update_service_price_table),
    ]
