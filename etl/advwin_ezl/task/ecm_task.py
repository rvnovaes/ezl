import os
import ntpath
from django.db.utils import IntegrityError
from django.db.models import  Q
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import traceback
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import ecm_path_advwin2ezl, get_message_log_default, save_error_log
from task.models import Ecm, Task, TaskStatus


class EcmEtl(GenericETL):
    _import_query = """
                    SELECT
                      G.ID_doc AS legacy_code,
                      A.Ident  AS task_legacy_code,
                      G.Link   AS path,
                      G.Nome as exhibition_name
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
                      G.ID_doc AS legacy_code,
                      A.Ident  AS task_legacy_code,
                      G.Link   AS path,
                      G.Nome as exhibition_name
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

    @staticmethod
    def list_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @property
    def import_query(self):
        status_list = [
            TaskStatus.DONE, TaskStatus.FINISHED, TaskStatus.REFUSED,
            TaskStatus.BLOCKEDPAYMENT, TaskStatus.REFUSED_SERVICE
        ]
        legacy_code_list = list(
            Task.objects.filter(legacy_code__isnull=False).exclude(
                legacy_code='REGISTRO-INVÁLIDO').exclude(
                    task_status__in=status_list).values_list(
                        'legacy_code', flat=True))
        legacy_code_list = list(self.list_chunks(legacy_code_list, 10))
        legacy_code_list_str = ''.join(
            map(lambda x: ' A.Ident IN (' + ', '.join(x) + ') OR',
                legacy_code_list))
        return self._import_query.format(
            task_list=legacy_code_list_str[:len(legacy_code_list_str) - 3])

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        """
        A importacao do ECM aramazena apenas o caminho com o nome do arquivo.
        Para que as duas aplicacacoes tenham acesso ao arquivo, e necessario que
        os dois tenham acesso ao mesmo servidor de arquivos.
        Para o EZL e necessario que a unidade do servidor de arquivos esteja montada no servidor
        linux. EX sudo mount -t cifs -o username=user //192.168.249.15/ged_advwin$ /mnt/windows_ecm/
        E necessario tambem criar um link simbolico com o nome ECM dentro do diretorio de
        MEDIA_ROOT apontando para /mnt/windows_ecm/Agenda.
        EX: sudo ln -s /mnt/windows_ecm/Agenda/ ./ECM
        """
        for row in rows:            
            try:
                path = ecm_path_advwin2ezl(row['path'])
                if path:
                    local_path = os.path.join(settings.MEDIA_ROOT, path)
                    if not os.path.exists(local_path):
                        continue
                    filename = ntpath.basename(local_path)                    

                    tasks = Task.objects.filter(
                        legacy_code=row['task_legacy_code'],
                        legacy_code__isnull=False)
                    for task in tasks:                        
                        try:
                            """
                            fazemos um select antes pelo path e pela task, já que um arquivo criado por um usuário, é 
                            exportado para o advwin, e lá ganha um legacy_code. Então, se checarmos pelo legacy_code os 
                            arquivos acabam sendo duplicados
                            https://ezlawyer.atlassian.net/browse/EZL-828
                            """
                            s3_filename = 'ECM/{0}/{1}'.format(task.pk, filename)
                            if not self.model.objects.filter(Q(task=task),
                                                             Q(
                                                                Q(path__endswith=filename) |
                                                                Q(exhibition_name=row['exhibition_name'])
                                                             )):
                                with open(local_path, 'rb') as local_file:
                                    new_file = ContentFile(local_file.read())
                                    new_file.name = filename                            

                                """
                                Caso o registro do arquivo não exista na base de dados e exista na S3 por algum motivo 
                                nao esperado, e necessario exclui-lo antes de inseri-lo novamente na base de dados, 
                                Se isso nao for feito ele sempre ira recriar o arquivo com um nome diferente que nunca 
                                se encaixara no filtro path__endswith, assim inserindo o arquivo toda vez que esta 
                                ETL rodar.
                                """
                                if default_storage.exists(s3_filename):
                                    default_storage.delete(s3_filename)
                                
                                self.model.objects.create(
                                    task=task,
                                    legacy_code=row['legacy_code'],
                                    system_prefix=LegacySystem.ADVWIN.value,
                                    is_active=True,
                                    path=new_file,
                                    create_user=user,
                                    alter_user=user,
                                    exhibition_name=row['exhibition_name'],
                                    updated=False)
                            self.debug_logger.debug(
                                'ECM,%s,%s,%s,%s'
                                % (str(row['legacy_code']),
                                   str(row['task_legacy_code']),
                                   str(row['path']), self.timestr))
                        except IntegrityError as e:
                            msg = get_message_log_default(
                                self.model._meta.verbose_name, rows_count,
                                traceback.format_exc(), self.timestr)
                            self.error_logger.error(msg)
                            save_error_log(log, user, msg)
            except Exception as e:
                msg = get_message_log_default(
                    self.model._meta.verbose_name, rows_count,
                    traceback.format_exc(), self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)
