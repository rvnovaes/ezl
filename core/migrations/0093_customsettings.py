# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-03 17:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0092_office_use_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('email_to_notification', models.EmailField(max_length=254, verbose_name='E-mail para receber notificações')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='customsettings_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='customsettings_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('office', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Office', verbose_name='Escritório')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
