# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-12 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_person_import_from_legacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='import_from_legacy',
            field=models.BooleanField(
                default=False, verbose_name='Importar OSs do sistema de origem para esse cliente'),
        ),
    ]
