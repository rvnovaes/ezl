# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction


def create_admin_settings(apps, schema_editor):
    AdminSettings = apps.get_model('core', 'adminsettings')
    with transaction.atomic():
        adminsettings = AdminSettings(rate_commission_correspondent=0.1, rate_commission_requestor=0.025)
        adminsettings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0142_auto_20190618_1004'),
    ]

    operations = [
        migrations.RunPython(create_admin_settings),
    ]
