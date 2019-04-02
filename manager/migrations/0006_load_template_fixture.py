# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2019-03-25 17:33
from __future__ import unicode_literals

from django.db import migrations
import logging
from django.core.management import call_command

logger = logging.getLogger('0005_migrate_custom_settings')


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'template', app_label='manager')


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_auto_20190326_1333'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
