# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-06 21:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0032_lawsuit_is_current_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courtdistrict',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='courtdistrict_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='courtdistrict',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courtdistrict_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='courtdivision',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='courtdivision_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='courtdivision',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courtdivision_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='folder_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='folder_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='instance_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instance_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='lawsuit',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lawsuit_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='lawsuit',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lawsuit_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='movement_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movement_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='typemovement_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='typemovement_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
    ]

    sql = "ALTER TABLE folder ADD COLUMN folder_number SERIAL NOT NULL;"

    operations.append(migrations.RunSQL(sql))
