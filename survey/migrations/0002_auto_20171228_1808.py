# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-28 20:08
from __future__ import unicode_literals

import os
from django.db import migrations

from survey.models import LEGACY_TYPES


NAMES = ["Operationlicense", "Diligence", "Protocol", "Courthearing"]


def _get_data(name):
    file_path = os.path.join(os.path.dirname(__file__), 'data/{}.json'.format(name))
    with open(file_path) as f:
        return f.read()


def populate_surveys(apps, schema_editor):
    Survey = apps.get_model('survey', 'Survey')

    for pk, name, title in LEGACY_TYPES:
        Survey.objects.create(id=pk, name=title, data=_get_data(name))


def remove_surveys(apps, schema_editor):
    Survey = apps.get_model('survey', 'Survey')
    Survey.objects.filter(name__in=NAMES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_surveys, remove_surveys),
    ]
