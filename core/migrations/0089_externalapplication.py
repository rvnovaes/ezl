# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-02 01:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oauth2_provider.generators
import oauth2_provider.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0088_auto_20180625_0551'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalApplication',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('client_id', models.CharField(db_index=True, default=oauth2_provider.generators.generate_client_id, max_length=100, unique=True)),
                ('redirect_uris', models.TextField(blank=True, help_text='Allowed URIs list, space separated', validators=[oauth2_provider.validators.validate_uris])),
                ('client_type', models.CharField(choices=[('confidential', 'Confidential'), ('public', 'Public')], max_length=32)),
                ('authorization_grant_type', models.CharField(choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials')], max_length=32)),
                ('client_secret', models.CharField(blank=True, db_index=True, default=oauth2_provider.generators.generate_client_secret, max_length=255)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('skip_authorization', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Office', verbose_name='Escritório')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_officeapplication', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
