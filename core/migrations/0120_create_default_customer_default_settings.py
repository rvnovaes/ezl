# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-11-07 17:33
from __future__ import unicode_literals

from django.db import migrations
from guardian.shortcuts import get_users_with_perms
import logging
logger = logging.getLogger('0118_create_default_customer_default_settings')


def create_custom_settings(apps, schema_editor):
    CustomSettings = apps.get_model('core', 'CustomSettings')
    Office = apps.get_model('core', 'Office')
    Person = apps.get_model('core', 'Person')
    OfficeMembership = apps.get_model('core', 'OfficeMembership')
    from django.contrib.auth.models import User
    admin = User.objects.get(username='admin')
    offices = Office.objects.all()
    total = offices.count()
    i = 0
    for office in offices:
        i += 1
        if not office.persons.filter(is_customer=True):
            default_customer, created = Person.objects.get_or_create(legal_name=office.legal_name,
                                                                     name=office.legal_name,
                                                                     is_customer=True,
                                                                     defaults={"create_user_id": admin.id})
            if created:
                OfficeMembership.objects.create(person=default_customer,
                                                office=office,
                                                create_user_id=admin.id,
                                                is_active=True)
            customsettings = getattr(office, 'customsettings', None)
            if customsettings and not customsettings.default_customer:
                customsettings.default_customer = default_customer
                customsettings.save()
            elif not customsettings:
                admin_group = [user for user, perms in get_users_with_perms(
                    office, attach_perms=True).items() if 'group_admin' in perms]
                default_user = admin_group[0] if admin_group else admin
                CustomSettings.objects.create(
                    office=office,
                    default_customer=default_customer,
                    default_user_id=default_user.id,
                    email_to_notification=default_user.email,
                    i_work_alone=False,
                    create_user_id=admin.id
                )
        logger.info('Escritório {} - {}/{}'.format(office.legal_name, i, total))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0119_customsettings_default_customer'),
    ]

    operations = [
        migrations.RunPython(create_custom_settings),
    ]
