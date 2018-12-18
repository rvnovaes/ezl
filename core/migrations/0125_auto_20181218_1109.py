# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-18 13:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0124_rename_office_offices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inviteoffice',
            options={'verbose_name': 'Convite para escritório', 'verbose_name_plural': 'Convites para escritórios'},
        ),
        migrations.AlterModelOptions(
            name='officeoffices',
            options={'ordering': ('from_office__legal_name', 'to_office__legal_name'), 'verbose_name': 'Relacionamento entre Escritórios', 'verbose_name_plural': 'Relacionamentos entre Escritórios'},
        ),
        migrations.AlterField(
            model_name='officeoffices',
            name='from_office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_offices', to='core.Office', verbose_name='Escritório de Origem'),
        ),
        migrations.AlterField(
            model_name='officeoffices',
            name='person_reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Person', verbose_name='Pessoa de Referência'),
        ),
        migrations.AlterField(
            model_name='officeoffices',
            name='to_office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_offices', to='core.Office', verbose_name='Escritório Relacionado'),
        ),
    ]
