# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-29 15:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0121_auto_20181023_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='typetask',
            name='survey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Survey', verbose_name='Formulário do correspondente'),
        ),
        migrations.AlterField(
            model_name='typetask',
            name='survey_company_representative',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='type_tasks_person_company_representative', to='survey.Survey', verbose_name='Formulário do preposto'),
        ),
    ]