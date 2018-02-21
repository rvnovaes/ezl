# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 12:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def remove_persons_from_office(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.filter(username='admin').first()
    if admin:
        Office = apps.get_model('core', 'Office')
        default_office = Office.objects.filter(create_user=admin,
                                               cpf_cnpj='03.482.042/0001-02',
                                               name='Marcelo Tostes Advogados Associados',
                                               legal_name='Marcelo Tostes Advogados Associados').first()

        for record in default_office.persons.all():
            default_office.persons.remove(record)

def populate_office_persons(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.filter(username='admin').first()
    if admin:
        Office = apps.get_model('core', 'Office')
        OfficeMembership = apps.get_model('core', 'OfficeMembership')
        default_office = Office.objects.filter(create_user=admin,
                                               cpf_cnpj='03.482.042/0001-02',
                                               name='Marcelo Tostes Advogados Associados',
                                               legal_name='Marcelo Tostes Advogados Associados').first()
        Person = apps.get_model('core', 'Person')
        persons_active = Person.objects.filter(is_active=True).all()
        OfficeMembership(office=default_office,
                         person=admin.person,
                         create_user=admin,
                         is_active=True,
                         create_date=timezone.now()).save()
        for person in persons_active:
            OfficeMembership(office=default_office,
                             person=person,
                             create_user=admin,
                             is_active=True,
                             create_date=timezone.now()).save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0072_auto_20180220_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficeMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alter_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='officemembership_alter_user', to=settings.AUTH_USER_MODEL, verbose_name='Alterado por')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='officemembership_create_user', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(remove_persons_from_office),
        migrations.RemoveField(
            model_name='office',
            name='persons',
        ),
        migrations.AddField(
            model_name='office',
            name='persons',
            field=models.ManyToManyField(blank=True, related_name='offices', through='core.OfficeMembership', to='core.Person'),
        ),
        migrations.AddField(
            model_name='officemembership',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Office'),
        ),
        migrations.AddField(
            model_name='officemembership',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Person'),
        ),
        migrations.RunPython(populate_office_persons),
    ]
