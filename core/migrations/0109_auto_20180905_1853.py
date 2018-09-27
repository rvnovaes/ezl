# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-05 21:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0108_emailtemplate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'verbose_name': 'E-mail templates'},
        ),
        migrations.AddField(
            model_name='customsettings',
            name='default_user',
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuário default'),
            preserve_default=False,
        ),
    ]
