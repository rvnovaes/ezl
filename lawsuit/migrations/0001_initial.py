# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-08 22:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeMovement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255)),
                ('legacy_code', models.CharField(max_length=255)),
                ('uses_wo', models.BooleanField(default=False)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='typemovement_alter_user', to=settings.AUTH_USER_MODEL)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='typemovement_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'type_movement',
            },
        ),
    ]
