from django.db.utils import IntegrityError

from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import ecm_path_advwin2ezl, get_users_to_import, get_message_log_default, save_error_log
from task.models import Ecm, Task


class EcmEtl(GenericETL):
    _import_query = """
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
                          AND G.Link <> ''
                          AND G.Link IS NOT NULL
                          AND cm.UsarOS = 1
                          AND (P.Status = 'Ativa' OR P.Status = 'Especial' OR p.Dt_Saida IS NULL)
                          (
                                (
                                    ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                                    (a.SubStatus = 80))
                                    AND 
                                    a.Advogado IN ('{person_legacy_code}')
                                )
                                OR
                                (
                                    (a.SubStatus = 10) OR 
                                    (a.SubStatus = 11) OR 
                                    (a.SubStatus = 20)
                                )
                          ) AND a.Status = '0' -- STATUS ATIVO
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
                          AND (p.Status = 'Ativa' OR p.Status = 'Especial')
                          AND G.Link <> ''
                          AND G.Link IS NOT NULL
                          AND cm.UsarOS = 1
                          (
                                (
                                    ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                                    (a.SubStatus = 80))
                                    AND 
                                    a.Advogado IN ('{person_legacy_code}')
                                )
                                OR
                                (
                                    (a.SubStatus = 10) OR 
                                    (a.SubStatus = 11) OR 
                                    (a.SubStatus = 20)
                                )
                          ) AND a.Status = '0' -- STATUS ATIVO
                          """
    model = Ecm
    field_check = 'ecm_legacy_code'

    @property
    def import_query(self):
        return self._import_query.format(person_legacy_code = "','".join(get_users_to_import()))

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
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
                            msg = get_message_log_default(
                                self.model._meta.verbose_name, rows_count, e,
                                self.timestr)
                            self.error_logger.error(msg)
                            save_error_log(log, user, msg)
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)
