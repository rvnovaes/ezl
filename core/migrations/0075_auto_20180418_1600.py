# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-04-18 16:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def add_admin_to_offices(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Office = apps.get_model('core', 'Office')
    OfficeMembership = apps.get_model('core', 'OfficeMembership')
    super_users = User.objects.filter(is_superuser=True).all()
    for super_user in super_users:
        super_user.groups.all().delete()
        offices = Office.objects.exclude(officemembership__person=super_user.person).all()
        for office in offices:
            OfficeMembership(office=office,
                             person=super_user.person,
                             create_user=super_user,
                             is_active=True,
                             create_date=timezone.now()).save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0074_auto_20180221_0933'),
        ('financial', '0014_change_correpondent_office_correspondent')
    ]

    operations = [
        migrations.RunPython(add_admin_to_offices),
    ]
