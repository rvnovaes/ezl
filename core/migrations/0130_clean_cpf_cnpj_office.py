# -*- coding: utf-8 -*-receate_offices_relations
# Created by Tiago Gomes 2019-02-04 14:48
from __future__ import unicode_literals

from django.db import migrations
from core.signals import create_office_custom_settings
from django.apps import apps


def clean_cpf_cnpj_office(apps, schema_editor):
    Office = apps.get_model('core', 'office')
    for office in Office.objects.all():
        try:
            office.save()
        except: 
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_auto_20190208_1310'),
    ]

    operations = [
        migrations.RunPython(clean_cpf_cnpj_office),
    ]
