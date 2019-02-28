# -*- coding: utf-8 -*-
# Created by Tiago Gomes on 2019-01-30 14:00
from __future__ import unicode_literals
from django.db import migrations
from django.db.models import Count, Max
import logging
logger = logging.getLogger('0032_service_price_table_policy_price')


def inactive_duplicated_records(apps, schema_editor):
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    unique_fields = ['office_correspondent', 'office_network', 'type_task', 'client', 'court_district', 'state',
                     'court_district_complement', 'office', 'city', 'value', 'policy_price']
    duplicates = ServicePriceTable.objects.filter(is_active=True)\
        .values(*unique_fields)\
        .order_by()\
        .annotate(max_id=Max('id'), count_id=Count('id'))\
        .filter(count_id__gt=1)

    for duplicate in duplicates:
            ServicePriceTable.objects\
                .filter(**{x: duplicate[x] for x in unique_fields})\
                .exclude(id=duplicate['max_id'])\
                .update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0039_update_value_to_pay_receive'),
    ]

    operations = [
        migrations.RunPython(inactive_duplicated_records),
    ]
