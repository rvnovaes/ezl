# -*- coding: utf-8 -*-
# Manually created by Tiago Gomes for Django 1.11.9 on 2018-02-28 10:54
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q
from etl.advwin_ezl.financial.cost_center import CostCenterETL
from etl.advwin_ezl.law_suit.folder import FolderETL
from financial.models import CostCenter
from lawsuit.models import Folder


class CostCenterETLUpdate(CostCenterETL):
    advwin_table = 'Jurid_Setor'
    model = CostCenter
    import_query = """
                SELECT DISTINCT
                  s.Codigo AS legacy_code,
                  s.Descricao
                FROM Jurid_Setor AS s
                      """
    has_status = True


class FolderETLUpdate(FolderETL):
    _import_query = """
            SELECT DISTINCT
              p.Codigo_Comp AS legacy_code,
              p.Cliente,
              p.Setor
            FROM Jurid_Pastas AS p
                  LEFT JOIN Jurid_ProcMov AS pm ON
                    pm.Codigo_Comp = p.Codigo_Comp
                  INNER JOIN Jurid_agenda_table AS a ON
                    a.Pasta = p.Codigo_Comp
                  INNER JOIN Jurid_CodMov AS cm ON
                    a.CodMov = cm.Codigo
            WHERE
                p.Codigo_Comp IN ('{folders}')
                    """

    @property
    def import_query(self):
        folder_list = list(Folder.objects.filter(~Q(id=1), Q(office_id=1),
                                                 Q(Q(cost_center__isnull=True) | Q(cost_center_id=1))
                                                 ).values_list('legacy_code', flat=True))
        return self._import_query.format(
            folders="','".join([f for f in folder_list if f]))


def update_cost_center(apps, schema_editor):
    from django.contrib.auth.models import User
    admin = User.objects.filter(username='admin').first()
    if not admin:
        return True
    generic_etl = CostCenterETLUpdate()
    CostCenterETLUpdate.import_data(generic_etl)
    generic_etl = FolderETLUpdate()
    FolderETLUpdate.import_data(generic_etl)


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0027_servicepricetable_policy_price'),
    ]

    operations = [
        migrations.RunPython(update_cost_center),
    ]
