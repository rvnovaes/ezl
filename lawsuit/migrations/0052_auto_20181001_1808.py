# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-01 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0113_auto_20180925_1126'),
        ('lawsuit', '0051_auto_20181001_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawsuit',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.City',
                                    verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='court_district_complement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='lawsuit_court_district_complement',
                                    to='lawsuit.CourtDistrictComplement', verbose_name='Complemento de comarca'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='performance_place',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Local de cumprimento'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='type_lawsuit',
            field=models.CharField(choices=[('ADMINISTRATIVE', 'Administrativo'), ('JUDICIAL', 'Judicial')],
                                   default='JUDICIAL', max_length=30, verbose_name='Tipo de processo'),
        ),
    ]