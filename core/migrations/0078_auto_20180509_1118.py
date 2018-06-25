# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-09 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_auto_20180509_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactmechanism',
            name='description',
            field=models.CharField(max_length=255, verbose_name='Descrição'),
        ),
        migrations.AlterUniqueTogether(
            name='contactmechanism',
            unique_together=set([('description', 'person'), ('description', 'office')]),
        ),
    ]
