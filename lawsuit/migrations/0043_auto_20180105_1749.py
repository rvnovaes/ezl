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
        default_office = Office.objects.get(
            create_user=admin,
            cpf_cnpj='03.482.042/0001-02',
            name='Marcelo Tostes Advogados Associados',
            legal_name='Marcelo Tostes Advogados Associados')
        CourtDivision = apps.get_model('lawsuit', 'courtdivision')
        for record in CourtDivision.objects.all():
            record.office_id = default_office.id
            record.save()

        Folder = apps.get_model('lawsuit', 'folder')
        for record in Folder.objects.all():
            record.office_id = default_office.id
            record.save()

        Instance = apps.get_model('lawsuit', 'instance')
        for record in Instance.objects.all():
            record.office_id = default_office.id
            record.save()

        LawSuit = apps.get_model('lawsuit', 'lawsuit')
        for record in LawSuit.objects.all():
            record.office_id = default_office.id
            record.save()

        Movement = apps.get_model('lawsuit', 'movement')
        for record in Movement.objects.all():
            record.office_id = default_office.id
            record.save()

        Organ = apps.get_model('lawsuit', 'organ')
        for record in Organ.objects.all():
            record.office_id = default_office.id
            record.save()

        TypeMovement = apps.get_model('lawsuit', 'typemovement')
        for record in TypeMovement.objects.all():
            record.office_id = default_office.id
            record.save()

        Sequence = apps.get_model('sequences', 'sequence')
        record = Sequence.objects.filter(
            name='lawsuit_folder_folder_number').first()
        if record:
            record.name = 'lawsuit_office_' + str(
                default_office.id) + '_folder_folder_number'
            record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_auto_20180221_0933'),
        ('lawsuit', '0042_auto_20180125_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtdivision',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='courtdivision_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='folder_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instance',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='instance_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='lawsuit_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movement',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='movement_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organ',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='organ_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='typemovement',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                null=True,
                related_name='typemovement_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.RunPython(get_default_office),
        migrations.AlterField(
            model_name='courtdivision',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='courtdivision_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='folder',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='folder_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='instance',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='instance_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lawsuit',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='lawsuit_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='movement',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='movement_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organ',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='organ_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='typemovement',
            name='office',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=False,
                null=False,
                related_name='typemovement_office',
                to='core.Office',
                verbose_name='Escritório'),
            preserve_default=False,
        ),
    ]
