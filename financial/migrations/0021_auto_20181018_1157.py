# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-18 14:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0020_servicepricetable_court_district_complement'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='servicepricetable',
            unique_together=set([]),
        ),
    ]
