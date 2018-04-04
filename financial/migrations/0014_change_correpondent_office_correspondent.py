# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-02-28 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def person_office(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.filter(username='admin').first()
    ServicePriceTable = apps.get_model('financial', 'ServicePriceTable')
    Office = apps.get_model('core', 'Office')
    OfficeMembership = apps.get_model('core', 'officemembership')
    for record in ServicePriceTable.objects.order_by('correspondent__id').all():
        person = record.correspondent
        person_office, created = Office.objects.get_or_create(create_user=admin,
                                                              cpf_cnpj=person.cpf_cnpj,
                                                              name=person.name,
                                                              legal_name=person.legal_name)
        OfficeMembership(office=person_office,
                         person=person,
                         create_user=admin,
                         is_active=True,
                         create_date=timezone.now()).save()
        record.office_correspondent = person_office
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0013_auto_20180214_1738'),
        ('core', '0073_auto_20180221_0933'),
    ]

    operations = [
        migrations.RunPython(person_office),
    ]
