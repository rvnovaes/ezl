# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-03 21:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0101_auto_20180903_1800'),
        ('core', '0105_customsettings_i_work_alone'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsettings',
            name='task_settings',
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='task.TaskSettings',
                verbose_name='workflow'),
            preserve_default=False,
        ),
    ]