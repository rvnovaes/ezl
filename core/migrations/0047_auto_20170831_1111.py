# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-31 14:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_modelexporthistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='address_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='address',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='address_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='addresstype',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='addresstype_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='addresstype',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='addresstype_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='city',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='city_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='city',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='city_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='contactmechanism',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactmechanism_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='contactmechanism',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactmechanism_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='contactmechanismtype',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactmechanismtype_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='contactmechanismtype',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactmechanismtype_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='contactus',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactus_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='contactus',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='contactus_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='country',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='country_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='country',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='country_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='person',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='person_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='person',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='person_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='state',
            name='alter_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='state_alter_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='state',
            name='create_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='state_create_user',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Criado por'),
        ),
    ]
