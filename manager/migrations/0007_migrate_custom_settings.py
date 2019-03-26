# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2019-03-25 17:33
from __future__ import unicode_literals

from django.db import migrations, transaction
import logging
from manager.template_values import ListTemplateValues
from manager.utils import update_template_value
from django.core.management import call_command

logger = logging.getLogger('0005_migrate_custom_settings')


def migrate_custom_settings(apps, schema_editor):
    from core.models import Office
    from django.contrib.auth.models import User
    admin = User.objects.get(username='admin')
    offices = Office.objects.all()
    total = offices.count()
    i = 0
    with transaction.atomic():
        for office in offices:
            i += 1
            customsettings = getattr(office, 'customsettings', None)
            if customsettings:
                office = customsettings.office
                default_customer_id = customsettings.default_customer_id
                email_notification = customsettings.email_to_notification
                i_work_alone = 'on' if customsettings.i_work_alone else ''
                default_user_id = customsettings.default_user_id
                use_etl = 'on' if office.use_etl_old else ''
                use_service = 'on' if office.use_service_old else ''

                values_by_template_key = {
                    'DEFAULT_CUSTOMER': default_customer_id,
                    'DEFAULT_USER': default_user_id,
                    'EMAIL_NOTIFICATION': email_notification,
                    'I_WORK_ALONE': i_work_alone,
                    'USE_SERVICE': use_service,
                    'USE_ETL': use_etl,
                }

                manager = ListTemplateValues(office)
                template_values = manager.instance_values
                for template_value in template_values:
                    new_value = values_by_template_key.get(template_value.value.get('template_key'))
                    update_template_value(template_value, new_value)

            logger.info('Escritório {} - {}/{}'.format(office.legal_name, i, total))
        call_command('test_migration_custom_settings')


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_load_template_fixture'),
        ('core', '0134_auto_20190326_1333'),
    ]

    operations = [
        migrations.RunPython(migrate_custom_settings),
    ]
