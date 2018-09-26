# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0013_chat_company'),
        ('task', '0090_auto_20180813_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='company_chat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_company_chat', to='chat.Chat', verbose_name='Chat Company'),
        ),
    ]
