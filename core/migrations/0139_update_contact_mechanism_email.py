# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2019-04-22 11:00
from __future__ import unicode_literals

from django.db import migrations, transaction


def updte_contact_mechanism(apps, schema_editor):
    ContactMechanismType = apps.get_model('core', 'contactmechanismtype')
    with transaction.atomic():
        ContactMechanismType.objects.filter(name='email').update(name='E-mail')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0138_auto_20190417_1411'),
    ]

    operations = [
        migrations.RunPython(updte_contact_mechanism),
    ]
