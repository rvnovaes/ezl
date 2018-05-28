from django.db.utils import IntegrityError

from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import ecm_path_advwin2ezl, get_message_log_default, save_error_log, \
    get_clients_to_import
from task.models import Ecm, Task, TaskStatus


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
                    WHERE {task_list}
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
                    WHERE {task_list}
                          """
    model = Ecm
    field_check = 'ecm_legacy_code'

    @staticmethod
    def list_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @property
    def import_query(self):
        status_list = [TaskStatus.DONE, TaskStatus.FINISHED, TaskStatus.REFUSED, TaskStatus.BLOCKEDPAYMENT,
                       TaskStatus.REFUSED_SERVICE]
        legacy_code_list = list(Task.objects.filter(legacy_code__isnull=False).exclude(legacy_code='REGISTRO-INVÁLIDO')
                                .exclude(task_status__in=status_list).values_list('legacy_code', flat=True))
        legacy_code_list = list(self.list_chunks(legacy_code_list, 10))
        legacy_code_list_str = ''.join(map(lambda x: ' A.Ident IN (' + ', '.join(x) + ') OR', legacy_code_list))
        return self._import_query.format(task_list=legacy_code_list_str[:len(legacy_code_list_str) - 3])

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
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
                path = ecm_path_advwin2ezl(row['path'])
                tasks = Task.objects.filter(legacy_code=row['task_legacy_code'])
                for task in tasks:
                    try:
                        self.model.objects.get_or_create(task=task,
                                                         legacy_code=row['ecm_legacy_code'],
                                                         system_prefix=LegacySystem.ADVWIN.value,
                                                         defaults={'is_active': True,
                                                                   'path': path,
                                                                   'create_user': user,
                                                                   'alter_user': user,
                                                                   'updated': False})
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
