# -*- coding: utf-8 -*-
# Created by Tiago Gomes on 2019-01-29 10:00
from __future__ import unicode_literals
from django.db import migrations
from financial.tasks import remove_special_char
import logging
logger = logging.getLogger('0037_service_price_table_type_task_office')


def update_service_price_table(apps, schema_editor):
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    for service_price in ServicePriceTable.objects.all().select_related('type_task', 'court_district_complement'):
        changed = False
        if service_price.type_task and service_price.office_id != service_price.type_task.office_id:
            name_service = remove_special_char(str(service_price.type_task.name).strip())
            type_task = service_price.office.typetask_office.filter(name__unaccent__iexact=name_service).first()
            service_price.type_task = type_task
            changed = True
        if service_price.court_district_complement and \
                service_price.court_district_complement.office_id != service_price.type_task.office_id:
            complement_name = remove_special_char(str(service_price.court_district_complement.name).strip())
            court_district_complement = service_price.office.courtdistrictcomplement_office.filter(
                name__unaccent__iexact=complement_name).first()
            service_price.court_district_complement = court_district_complement
            changed = True
        if changed:
            service_price.save()
        logging.info('ALTERADO TIPO DE PRECO NA TABLEA DE PRECOS: ID-{}'.format(service_price.pk))


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0036_auto_20190121_1205'),
    ]

    operations = [
        migrations.RunPython(update_service_price_table),
    ]
