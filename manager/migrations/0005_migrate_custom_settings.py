# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-11-07 17:33
from __future__ import unicode_literals

from django.db import migrations
import logging
from manager.template_values import ListTemplateValues
from manager.utils import update_template_value

logger = logging.getLogger('0118_create_default_customer_default_settings')


def migrate_custom_settings(apps, schema_editor):
    Office = apps.get_model('core', 'Office')
    from django.contrib.auth.models import User
    admin = User.objects.get(username='admin')
    offices = Office.objects.all()
    total = offices.count()
    i = 0
    default_customer_id = None
    email_notification = None
    i_work_alone = None
    default_user_id = None
    use_etl = None
    use_service = None
    values_by_template_key = {
        'DEFAULT_CUSTOMER': default_customer_id,
        'DEFAULT_USER': default_user_id,
        'EMAIL_NOTIFICATION': email_notification,
        'I_WORK_ALONE': i_work_alone,
        'USE_SERVICE': use_service,
        'USE_ETL': use_etl,
    }
    for office in offices:
        i += 1
        customsettings = getattr(office, 'customsettings', None)
        if customsettings:
            office = customsettings.office
            default_customer_id = customsettings.default_customer_id
            email_notification = customsettings.email_to_notification
            i_work_alone = customsettings.i_work_alone
            default_user_id = customsettings.default_user_id
            use_etl = office.use_etl,
            use_service = office.use_service

            manager = ListTemplateValues(office)
            template_values = manager.instance_values
            for template_value in template_values:
                new_value = values_by_template_key.get(template_value.value.get('template_key'))
                if new_value:
                    update_template_value(template_value, new_value)

        logger.info('Escritório {} - {}/{}'.format(office.legal_name, i, total))


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_auto_20190325_1442'),
    ]

    operations = [
        migrations.RunPython(migrate_custom_settings),
    ]
