# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-23 18:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('core', '0072_auto_20180220_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficeRelGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='office_groups', to='core.Office')),
            ],
            options={
                'verbose_name': 'Groupos por escritório',
            },
        ),
    ]
