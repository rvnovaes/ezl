# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-31 15:06
from __future__ import unicode_literals

from django.db import migrations, models
import lawsuit.models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0035_auto_20170831_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='folder_number',
            field=models.IntegerField(default=lawsuit.models.Folder.increment, editable=False, null=True, verbose_name='Número da Pasta'),
        ),
    ]
