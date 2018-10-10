# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-03 19:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0115_task_performance_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcmTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ecm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task.Ecm')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task.Task')),
            ],
        ),
        migrations.AddField(
            model_name='ecm',
            name='tasks',
            field=models.ManyToManyField(related_name='_ecm_tasks_+', through='task.EcmTask', to='task.Task'),
        ),
    ]