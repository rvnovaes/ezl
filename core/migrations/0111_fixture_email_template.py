# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-09-17 13:40
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'email_template', app_label='core')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0110_importxlsfile'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
