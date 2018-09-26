# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-05 19:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def get_default_office(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.filter(username='admin').first()
    if admin:
        Office = apps.get_model('core', 'Office')
        default_office = Office.objects.get(create_user=admin,
                                            cpf_cnpj='03.482.042/0001-02',
                                            name='Marcelo Tostes Advogados Associados',
                                            legal_name='Marcelo Tostes Advogados Associados')
        Dashboardetl = apps.get_model('etl', 'dashboardetl')
        for record in Dashboardetl.objects.all():
            record.office_id = default_office.id
            record.save()

        Inconsistencyetl = apps.get_model('etl', 'inconsistencyetl')
        for record in Inconsistencyetl.objects.all():
            record.office_id = default_office.id
            record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_auto_20180221_0933'),
        ('etl', '0011_inconsistencyetl'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardetl',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, null=True,
                                    related_name='dashboardetl_office', to='core.Office', verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inconsistencyetl',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, null=True,
                                    related_name='inconsistencyetl_office', to='core.Office',
                                    verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.RunPython(get_default_office),
        migrations.AlterField(
            model_name='dashboardetl',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=False, null=False,
                                    related_name='dashboardetl_office', to='core.Office', verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inconsistencyetl',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=False, null=False,
                                    related_name='inconsistencyetl_office', to='core.Office',
                                    verbose_name='Escritório'),
            preserve_default=False,
        ),
    ]
