# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-10-29 17:33
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command
from guardian.shortcuts import get_users_with_perms


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'email_template', app_label='core')


def create_custom_settings(apps, schema_editor):
    from core.models import CustomSettings, Office
    offices = Office.objects.all()
    for office in offices:
        admin_group = [user for user, perms in get_users_with_perms(
            office, attach_perms=True).items() if 'group_admin' in perms]
        if admin_group:
            default_user = admin_group[0]
            CustomSettings.objects.get_or_create(
                office=office,
                defaults={'default_user': default_user,
                          'email_to_notification': default_user.email,
                          'i_work_alone': False,
                          'create_user_id': 2}
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0115_auto_20181029_1749'),
        ('task', '0126_taskshowstatus_mail_recipients'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
        migrations.RunPython(create_custom_settings),
    ]
