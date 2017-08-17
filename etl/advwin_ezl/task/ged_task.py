# esse import deve vir antes de todos porque ele executa o __init__.py
import ntpath
import os

import paramiko

from core.utils import LegacySystem
from etl.advwin_ezl import settings
from etl.advwin_ezl.advwin_ezl import GenericETL
from task.models import Ecm
from task.models import Task


class EcmETL(GenericETL):
    import_query = "SELECT " \
                   "   G.ID_doc, " \
            "   A.Ident,   " \
            "   G.Link      " \
            " FROM Jurid_Ged_Main AS G" \
            " INNER JOIN Jurid_agenda_table AS A" \
            "   ON G.Codigo_OR = CAST(A.Ident as VARCHAR(255)) " \
            " INNER JOIN  Jurid_Pastas AS P" \
            "   ON A.Pasta = P.Codigo_Comp" \
            "  WHERE G.Tabela_OR = 'Agenda' AND P.Status = 'Ativa' AND G.Link <> '' AND G.Link IS NOT NULL"

    model = Ecm
    advwin_table = 'Jurid_Ged_Main'
    has_status = False

    def config_import(self, rows, user, rows_count):

        # paramiko.util.log_to_file(settings.log_file)
        transport = paramiko.Transport((settings.host_sftp, settings.port_sftp))
        transport.connect(username=settings.username_sftp, password=settings.password_sftp)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_path = ''
        local_path = ''

        for row in rows:

            path = row['Link']

            # O advwin armazena o path dos arquivos que não foram feitos checkin. Padrão dos paths (C:/caminho)
            # O padrão dos arquivos feitos checkin é: \\172.27.155.11\ged_advwin$\Agenda\MTA012985638_V1.pdf
            # Assim só é importado arquivos cujo path começa com '\'

            if path[0] is not '\\':
                print('Path inválido')
                is_server = False

            else:
                is_server = True

            # Alguns registros de GED não contém um path, é NULL no banco. Assim, só é importando registros
            # que possuem um path válido

            if path and is_server:
                print('Registros restantes: ' + str(rows_count))
                file = ntpath.basename(path)
                rows_count -= 1
                ecm_legacy_code = row['ID_doc']
                task_legacy_code = row['Ident']

                # Um GED criado no EZL (sem legacy_code) e que já constado no Advwin, neste arquivo será lançado
                # um erro ao tentar adicionar os dados no arquivo no banco de dados, pois os Patchs seriam identicos.
                # Assim, só adiciona um novo registro caso não haja outro como o mesmo Patch
                id_task = Task.objects.get(legacy_code=task_legacy_code).id
                is_ecm = False
                if self.model.objects.filter(path__unaccent='GEDs/' + str(id_task) + '/' + file):
                    is_ecm = True

                task = Task.objects.filter(legacy_code=task_legacy_code).first()
                ecm = self.model.objects.filter(legacy_code=ecm_legacy_code, task=task,
                                                system_prefix=LegacySystem.ADVWIN.value).first() if task else None
                if ecm:
                    pass
                    # Remove o arquivo para depois importar novamente, em caso de atualização do mesmo
                    # os.remove(ezl_settings.MEDIA_ROOT + str(ecm.path))
                    # ecm.path = 'GEDs/' + str(task.id) + '/' + file
                    # ecm.task = task
                    # ecm.is_active = True
                    # ecm.alter_user = user
                    # ecm.updated = False
                    # ecm.save(update_fields=[
                    #     'path',
                    #     'task',
                    #     'is_active',
                    #     'alter_user',
                    #     'alter_date',
                    #     'updated'])

                elif task and not is_ecm:
                    ecm = self.model(path='GEDs/' + str(task.id) + '/' + file,
                                     task=task,
                                     is_active=True,
                                     legacy_code=ecm_legacy_code,
                                     system_prefix=LegacySystem.ADVWIN.value,
                                     create_user=user,
                                     alter_user=user,
                                     updated=False
                                     )
                    ecm.save()

                # Apenas obtem o arquivo via SFTP caso não haja nenhum GED cadastrado
                if task and not is_ecm and path:
                    is_file = False
                    # Deve verificar se o arquivo está contido no diretório de GEDs do Advwin. Pois existem caminhos
                    # de arquivos no banco mas não contém o arquivo no sistema de arquivos
                    try:
                        sftp.stat('Agenda\\' + file)
                        is_file = True
                        remote_path = 'Agenda\\' + file
                    except:

                        try:
                            sftp.stat('Agenda\\' + str(task_legacy_code) + '\\' + file)
                            remote_path = 'Agenda\\' + str(task_legacy_code) + '\\' + file
                            is_file = True
                        except:
                            is_file = False
                            print('erro no arquivo')

                    if is_file:
                        import_dir = settings.local_path + str(task.id) + '/'

                        # Se não houver nenhum diretório com o ID da task, cria um novo
                        if not os.path.exists(import_dir):
                            os.makedirs(import_dir)

                        print('Importando arquivo ' + file + ' ... ')
                        sftp.get(remote_path, import_dir + file, callback=None)
        sftp.close()


if __name__ == "__main__":
    EcmETL().import_data()
