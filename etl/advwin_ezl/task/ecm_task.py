#!/usr/bin/python
# -*- encoding: utf-8 -*-
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from django.db.utils import IntegrityError
from task.models import Ecm, Task


class EcmEtl(GenericETL):
    import_query = """
                SELECT
                  G.ID_doc AS ecm_legacy_code,
                  A.Ident  AS task_legacy_code,
                  G.Link   AS path
                FROM Jurid_Ged_Main AS G
                  INNER JOIN Jurid_agenda_table AS A
                    ON G.Codigo_OR = CAST(A.Ident AS VARCHAR(255))
                  INNER JOIN Jurid_Pastas AS P
                    ON A.Pasta = P.Codigo_Comp
                  INNER JOIN Jurid_CodMov AS cm
                    ON A.CodMov = cm.Codigo
                WHERE G.Tabela_OR = 'Agenda'
                      AND P.Status = 'Ativa'
                      AND G.Link <> ''
                      AND G.Link IS NOT NULL
                      AND cm.UsarOS = 1
                      AND (p.Status = 'Ativa' OR p.Dt_Saida IS NULL)
                      AND ((a.prazo_lido = 0 AND a.SubStatus = 30) OR (a.SubStatus = 80 AND a.Status = 0))
    """
    model = Ecm

    def config_import(self, rows, user, rows_count):
        """
        A importacao do ECM aramazena apenas o caminho com o nome do arquivo.
        Para que as duas aplicacacoes tenham acesso ao arquivo, e necessario que
        os dois tenham acesso ao mesmo servidor de arquivos.
        Para o EZL e necessario que a unidade do servidor de arquivos esteja montada no servidor
        linux. EX sudo mount -t cifs -o username=user //172.27.155.11/ged_advwin$ /mnt/windows_ecm/
        E necessario tambem criar um link simbolico com o nome ECM dentro do diretorio de
        MEDIA_ROOT apontando para /mnt/windows_ecm/Agenda.
        EX: sudo ln -s /mnt/windows_ecm/Agenda/ ./ECM
        """
        for row in rows:
            try:
                if 'Agenda' in row['path']:
                    path = 'ECM/' + row['path'].split('Agenda\\')[1].replace('\\', '/')
                    tasks = Task.objects.filter(legacy_code=row['task_legacy_code'])
                    for task in tasks:
                        try:
                            ecm = self.model(path=path, task=task, is_active=True,
                                             legacy_code=row['ecm_legacy_code'],
                                             system_prefix=LegacySystem.ADVWIN.value,
                                             create_user=user,
                                             alter_user=user, updated=False)
                            ecm.save()
                            self.debug_logger.debug(
                                "ECM,%s,%s,%s,%s" % (
                                    str(row['ecm_legacy_code']), str(row['task_legacy_code']),
                                    str(row['path']), self.timestr))
                        except IntegrityError as e:
                            print(e)
            except Exception as e:
                self.error_logger.error(
                    "Ocorreu o seguinte erro na importacao de ECM: " + str(rows_count) + "," + str(
                        e) + "," + self.timestr)
