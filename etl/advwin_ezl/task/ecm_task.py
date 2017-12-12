from django.db.utils import IntegrityError

from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from etl.utils import ecm_path_advwin2ezl, get_users_to_import
from task.models import Ecm, Task


class EcmEtl(GenericETL):
    def __init__(self, task_legacy_code=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_legacy_code = task_legacy_code
        if self.task_legacy_code:
            self.import_query = self.get_sql_filter_task()
        else:
            self.import_query = self.get_query_all()
    model = Ecm

    @property
    def import_query(self):
        return self._import_query.format("','".join(get_users_to_import()))

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
            print(row)
            try:
                if 'Agenda' in row['path']:
                    path = ecm_path_advwin2ezl(row['path'])
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
                                'ECM,%s,%s,%s,%s' % (
                                    str(row['ecm_legacy_code']), str(row['task_legacy_code']),
                                    str(row['path']), self.timestr))
                        except IntegrityError as e:
                            print(e)
            except Exception as e:
                self.error_logger.error(
                    'Ocorreu o seguinte erro na importacao de ECM: ' + str(rows_count) + ',' + str(
                        e) + ',' + self.timestr)


    def get_query_all(self):
        sql = """
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
                          AND ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                               (a.SubStatus = 80)) AND a.Status = '0' -- STATUS ATIVO
                          AND a.Advogado IN ('12157458697', '12197627686', '13281750656', '11744024000171', '20010149000165', '01605132608')
                    UNION
                    SELECT DISTINCT
                      G.ID_doc AS ecm_legacy_code,
                      A.Ident  AS task_legacy_code,
                      G.Link   AS path
                    FROM Jurid_Ged_Main AS G
                      INNER JOIN Jurid_GEDLig AS GL
                        ON GL.Id_id_doc = G.ID_doc
                      INNER JOIN Jurid_agenda_table AS A
                        ON GL.Id_codigo_or = CAST(A.Ident AS VARCHAR(255))
                      INNER JOIN Jurid_Pastas AS P
                        ON A.Pasta = P.Codigo_Comp
                      INNER JOIN Jurid_CodMov AS cm
                        ON A.CodMov = cm.Codigo
                    WHERE GL.Id_tabela_or = 'Agenda'
                          AND P.Status = 'Ativa'
                          AND G.Link <> ''
                          AND G.Link IS NOT NULL
                          AND cm.UsarOS = 1
                          AND (p.Status = 'Ativa' OR p.Dt_Saida IS NULL)
                          AND ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                               (a.SubStatus = 80)) AND a.Status = '0' -- STATUS ATIVO
                          AND a.Advogado IN ('{}')
                          """
        return sql

    def get_sql_filter_task(self):
        sql = """
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
                    WHERE A.Ident = {task}
                    UNION ALL
                    SELECT DISTINCT
                      G.ID_doc AS ecm_legacy_code,
                      A.Ident  AS task_legacy_code,
                      G.Link   AS path
                    FROM Jurid_Ged_Main AS G
                      INNER JOIN Jurid_GEDLig AS GL
                        ON GL.Id_id_doc = G.ID_doc
                      INNER JOIN Jurid_agenda_table AS A
                        ON GL.Id_codigo_or = CAST(A.Ident AS VARCHAR(255))
                      INNER JOIN Jurid_Pastas AS P
                        ON A.Pasta = P.Codigo_Comp
                      INNER JOIN Jurid_CodMov AS cm
                        ON A.CodMov = cm.Codigo
                    WHERE A.Ident = {task}
        """.format(task=self.task_legacy_code)
        return sql
