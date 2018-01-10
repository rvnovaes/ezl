# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-04 19:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0055_auto_20180104_1731'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-alter_date'], 'permissions': [('view_delegated_tasks', 'Can view tasks delegated to the user'), ('view_all_tasks', 'Can view all tasks'), ('return_all_tasks', 'Can return tasks'), ('validate_all_tasks', 'Can validade tasks'), ('view_requested_tasks', 'Can view tasks requested by the user'), ('block_payment_tasks', 'Can block tasks payment'), ('can_access_general_data', 'Can access general data screens'), ('view_distributed_tasks', 'Can view tasks distributed by the user'), ('can_distribute_tasks', 'Can distribute tasks to another user')], 'verbose_name': 'Providência', 'verbose_name_plural': 'Providências'},
        ),
        migrations.AlterField(
            model_name='task',
            name='chat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.Chat', verbose_name='Chat'),
        ),
    ]
