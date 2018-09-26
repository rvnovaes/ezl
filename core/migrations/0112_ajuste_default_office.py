# -*- coding: utf-8 -*-
# Created by Tiago Gomes 2018-09-17 13:40
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('0112_ajuste_default_office')


def remove_invalid_default_office(apps, schema_editor):    
    from core.models import DefaultOffice   
    for user in User.objects.all():
        try:
            if not user.person.offices.active_offices().filter(pk=user.defaultoffice.office.pk).exists():
                user.defaultoffice.delete()
                if len(user.person.offices.active_offices()) == 1: 
                    defaultoffice = DefaultOffice(
                        create_user_id=user.pk, auth_user=user, office=user.person.offices.active_offices().first())
                    defaultoffice.save()
                logger.info('AJUSTADO USUARIO {}'.format(user.username))
        except:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0111_fixture_email_template'),
    ]

    operations = [
        migrations.RunPython(remove_invalid_default_office),
    ]
