# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-17 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['-id'], 'verbose_name': 'Person'},
        ),
        migrations.AlterField(
            model_name='person',
            name='legal_type',
            field=models.CharField(choices=[('F', 'Física'), ('J', 'Jurídica')], max_length=1),
        ),
    ]
