# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-11-07 17:33
from __future__ import unicode_literals

from django.db import migrations
import logging
# logger = logging.getLogger('0118_create_default_customer_default_settings')


def recreate_offices_relations(apps, schema_editor):
    Office = apps.get_model('core', 'Office')
    OfficeOffices = apps.get_model('core', 'OfficeOffices')
    from django.contrib.auth.models import User
    admin = User.objects.get(username='admin')
    offices = Office.objects.all()
    total = offices.count()
    i = 0
    create_list = []
    if admin:
        for office in offices:
            for office_related in office.offices.all():
                create_list.append(OfficeOffices(from_office=office,
                                                 to_office=office_related,
                                                 create_user_id=2))
        # logger.info('Escritório {} - {}/{}'.format(office.legal_name, i, total))
        OfficeOffices.objects.bulk_create(create_list)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0124_auto_20181217_1120'),
    ]

    operations = [
        migrations.RunPython(recreate_offices_relations),
    ]
