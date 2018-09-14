# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-20 17:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('lawsuit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='court_district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='lawsuit.CourtDistrict', verbose_name='Comarca'),
        ),
        migrations.AddField(
            model_name='city',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name='city_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.State'),
        ),
        migrations.AddField(
            model_name='addresstype',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='addresstype_alter_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='addresstype',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name='addresstype_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='address_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.AddressType'),
        ),
        migrations.AddField(
            model_name='address',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='address_alter_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.City'),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.Country'),
        ),
        migrations.AddField(
            model_name='address',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name='address_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='person',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.Person'),
        ),
        migrations.AddField(
            model_name='address',
            name='state',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='core.State'),
        ),
    ]
