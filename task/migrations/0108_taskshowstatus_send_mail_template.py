# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-06 17:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0109_auto_20180905_1853'),
        ('task', '0107_remove_taskworkflow_send_mail_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskshowstatus',
            name='send_mail_template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.EmailTemplate',
                verbose_name='Template a enviar'),
        ),
    ]
