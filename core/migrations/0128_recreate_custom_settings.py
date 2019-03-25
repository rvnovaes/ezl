# -*- coding: utf-8 -*-receate_offices_relations
# Created by Tiago Gomes 2019-02-04 14:48
from __future__ import unicode_literals

from django.db import migrations
from core.signals import create_office_setting_default_customer


def recreate_custom_settings(apps, schema_editor):
    Office = apps.get_model('core', 'Office')
    offices = Office.objects.filter(customsettings__isnull=True)
    for office in offices:
        create_office_setting_default_customer(office, False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0127_auto_20181218_1109'),
    ]

    operations = [
        migrations.RunPython(recreate_custom_settings),
    ]
