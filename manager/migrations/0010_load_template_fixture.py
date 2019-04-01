# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2019-03-25 17:33
from __future__ import unicode_literals

from django.db import migrations
import logging
from django.core.management import call_command

logger = logging.getLogger('0010_load_template_fixture')


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'template', app_label='manager')


def update_mta(apps, schema_editor):
    from manager.enums import TemplateKeys
    from manager.utils import update_template_value
    from etl.utils import get_default_office
    office = get_default_office()
    template_obj = office.get_template_value_obj(TemplateKeys.DUPLICATE_PROCESS.name)
    update_template_value(template_obj, str(2))


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0009_load_template_fixture'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
        migrations.RunPython(update_mta),
    ]
