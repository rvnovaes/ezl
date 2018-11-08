# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-24 18:04
from __future__ import unicode_literals

from django.db import migrations, models
import task.models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0125_auto_20181025_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskshowstatus',
            name='mail_recipients',
            field=task.models.ChoiceArrayField(base_field=models.CharField(choices=[('PERSON_ASKED_BY', 'Solicitante'), ('PERSON_EXECUTED_BY', 'Correspondente'), ('PERSON_DISTRIBUTED_BY', 'Contratante'), ('PARENT_OFFICE', 'Escritório Contratante'), ('CHILD_OFFICE', 'Escritório Correspondente'), ('NONE', 'Nenhum')], max_length=256, null=True, verbose_name='Destinatários do e-mail'), default=[], size=None),
        ),
    ]