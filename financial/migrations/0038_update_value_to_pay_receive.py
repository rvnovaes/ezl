# -*- coding: utf-8 -*-
# Created by Tiago Gomes on 2019-01-30 14:00
from __future__ import unicode_literals
from django.db import migrations
from django.db.models import F
import logging
logger = logging.getLogger('0032_service_price_table_policy_price')


def update_service_price_table(apps, schema_editor):
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    ServicePriceTable.objects.update(value_to_pay=F('value'), value_to_receive=F('value'))


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0037_auto_20190131_1343'),
    ]

    operations = [
        migrations.RunPython(update_service_price_table),
    ]
