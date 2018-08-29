# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-29 13:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0047_auto_20180731_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawsuit',
            name='court_division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='court_divisions', to='lawsuit.CourtDivision', verbose_name='Vara'),
        ),
        migrations.AlterField(
            model_name='lawsuit',
            name='person_lawyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='person_lawyers', to='core.Person', verbose_name='Advogado'),
        ),
    ]
