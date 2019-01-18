# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-12 13:19
from __future__ import unicode_literals
from django.db import migrations, models
import logging
logger = logging.getLogger('0030_policy_price_default')


def create_default_policy(apps, schema_editor):
    from financial.models import CategoryPrice, BillingMoment
    from django.contrib.auth.models import User
    PolicyPrice = apps.get_model('financial', 'PolicyPrice')
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    Office = apps.get_model('core', 'Office')
    policys_price = []
    admin_user = User.objects.get(username='admin')    
    # Criando politicas de preco
    for office in Office.objects.all():
        policy_pre_paid = PolicyPrice(
            office=office, 
            create_user_id=admin_user.pk,
            name='Pré-Pago',
            category=CategoryPrice.PREPAID,
            billing_moment=BillingMoment.PRE_PAID)
        policys_price.append(policy_pre_paid)
        policy_post_paid = PolicyPrice(
            office=office,
            create_user_id=admin_user.pk,
            name='Pós-Pago',
            category=CategoryPrice.POSTPAID,
            billing_moment=BillingMoment.POST_PAID)
        policys_price.append(policy_post_paid)
        policy_public = PolicyPrice(
            office=office, 
            create_user_id=admin_user.pk,
            name='Público',
            category=CategoryPrice.PUBLIC,
            billing_moment=BillingMoment.PRE_PAID
        )
        policys_price.append(policy_public)
        policy_network = PolicyPrice(
            office=office,
            create_user_id=admin_user.pk,
            name='Rede',
            category=CategoryPrice.NETWORK,
            billing_moment=BillingMoment.PRE_PAID
        )
        policys_price.append(policy_network)
        logging.info('CRIADO TIPOS DE PRECO PARA O ESCRITORIO {}'.format(office.legal_name))
    PolicyPrice.objects.bulk_create(policys_price)


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0029_servicepricetable_policy_price'),
    ]

    operations = [
        migrations.RunPython(create_default_policy),
    ]
