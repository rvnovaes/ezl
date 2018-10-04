# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-24 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0014_auto_20180824_1523'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userbychat',
            index=models.Index(
                fields=['user_by_chat_id'],
                name='chat_userby_user_by_403017_idx'),
        ),
    ]