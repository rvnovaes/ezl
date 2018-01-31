# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-08 20:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

def get_default_office(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.filter(username='admin').first()
    if admin:
        Office = apps.get_model('core', 'Office')
        default_office, created = Office.objects.get_or_create(create_user=admin,
                                                               cpf_cnpj='03.482.042/0001-02',
                                                               name='Marcelo Tostes Advogados Associados',
                                                               legal_name='Marcelo Tostes Advogados Associados')
        ServicePriceTable = apps.get_model('financial', 'servicepricetable')
        for record in ServicePriceTable.objects.all():
            record.office_id = default_office.id
            record.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0057_merge_20180108_1756'),
        ('financial', '0005_auto_20180112_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicepricetable',
            name='alter_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em'),
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='servicepricetable_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por'),
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Criado em'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='create_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='servicepricetable_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='legacy_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Código legado'),
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='system_prefix',
            field=models.CharField(blank=True, choices=[('Advwin', 'Advwin')], max_length=255, null=True, verbose_name='Prefixo do sistema'),
        ),
        migrations.AddField(
            model_name='servicepricetable',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, null=True,
                                    related_name='servicepricetable_office', to='core.Office',
                                    verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.RunPython(get_default_office),
        migrations.AlterField(
            model_name='servicepricetable',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name='servicepricetable_office', to='core.Office',
                                    verbose_name='Escritório'),
            preserve_default=False,
        ),
    ]
