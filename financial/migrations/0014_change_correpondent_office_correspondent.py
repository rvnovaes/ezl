# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-02-28 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from core.permissions import create_permission
from guardian.shortcuts import get_groups_with_perms


def person_office(apps, schema_editor):
    from django.contrib.auth.models import User
    from core.models import Office, OfficeMembership
    from financial.models import ServicePriceTable
    admin = User.objects.filter(username='admin').first()
    if not admin:
        return True
    office_mt = Office.objects.filter(cpf_cnpj='03.482.042/0001-02').last()
    if not office_mt:
        return True

    for record in ServicePriceTable.objects.order_by('correspondent__id').all():
        person = record.correspondent
        create_user = User.objects.get(pk=person.auth_user.pk) if person.auth_user else admin
        person_office, created = Office.objects.get_or_create(create_user=create_user,
                                                              cpf_cnpj=person.cpf_cnpj,
                                                              name=person.name,
                                                              legal_name=person.legal_name)
        if created:
            office_mt.offices.add(person_office)
            create_permission(person_office)
            for group in {group for group, perms in
                          get_groups_with_perms(person_office, attach_perms=True).items() if 'group_admin' in perms}:
                create_user.groups.add(group)
            OfficeMembership(office=person_office,
                             person=person,
                             create_user=create_user,
                             is_active=True,
                             create_date=timezone.now()).save()
        record.office_correspondent = person_office
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0013_auto_20180214_1738'),
        ('core', '0074_auto_20180221_0933'),
    ]

    operations = [
        migrations.RunPython(person_office),
    ]
