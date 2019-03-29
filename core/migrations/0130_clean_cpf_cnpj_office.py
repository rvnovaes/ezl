# -*- coding: utf-8 -*-receate_offices_relations
# Created by Tiago Gomes 2019-02-04 14:48
from __future__ import unicode_literals

from django.db import migrations
from core.signals import create_office_setting_default_customer
from django.apps import apps
import re
import logging
from django.db import transaction

LOGGER = logging.getLogger('0130_clean_cpf_cnpj_office')

def clear_cpf_cnpj(cpf_cnpj):
    return re.sub(r'[^0-9]', '', cpf_cnpj)


def clean_cpf_cnpj_office(apps, schema_editor):
    Office = apps.get_model('core', 'office')
    for office in Office.objects.all():
        if office.cpf_cnpj:
            office.cpf_cnpj = clear_cpf_cnpj(office.cpf_cnpj)
            with transaction.atomic():
                try:
                    office.save()
                except Exception as e:
                    LOGGER.info('ERRO AO ATUALIZAR CPF/CNPJ DE {} - {}'.format(
                        office.legal_name, office.cpf_cnpj))            


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_auto_20190208_1310'),
    ]

    operations = [
        migrations.RunPython(clean_cpf_cnpj_office),
    ]
