# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-04 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_remove_customsettings_task_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nome do template')),
                ('template_id', models.CharField(max_length=255, verbose_name='Id do tempĺate (sendgrid)')),
            ],
        ),
    ]
