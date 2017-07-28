# esse import deve vir antes de todos porque ele executa o __init__.py
from etl.advwin_ezl.advwin_ezl import GenericETL
import os
from core.utils import LegacySystem
from task.models import Ecm
from task.models import Task
import paramiko
from etl.advwin_ezl import settings
from ezl import settings as ezl_settings


class EcmETL(GenericETL):
    query = "SELECT " \
            "   G.ID_doc, " \
            "   A.Ident,   " \
            "   G.Link      " \
            " FROM Jurid_Ged_Main AS G" \
            " INNER JOIN Jurid_agenda_table AS A" \
            "   ON G.Codigo_OR = CAST(A.Ident as VARCHAR(255)) AND A.Ident = 2254248 " \
            " INNER JOIN  Jurid_Pastas AS P" \
            "   ON A.Pasta = P.Codigo_Comp" \
            "  WHERE G.Tabela_OR = 'Agenda' AND P.Status = 'Ativa' AND G.Link <> '' AND G.Link IS NOT NULL"

    model = Ecm
    advwin_table = 'Jurid_Ged_Main'
    has_status = False

    def load_etl(self, rows, user, rows_count):

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
                print(rows_count)
                file = path.strip(str('\\172.27.155.11\\ged_advwin$\\Agenda\\'))
                remote_path = 'Agenda/' + file
                rows_count -= 1
                ecm_legacy_code = row['ID_doc']
                task_legacy_code = row['Ident']

                task = Task.objects.filter(legacy_code=task_legacy_code).first()

                ecm = self.model.objects.filter(legacy_code=ecm_legacy_code, task=task,
                                                system_prefix=LegacySystem.ADVWIN.value).first() if task else None

                if ecm:

                    # Remove o arquivo para depois importar novamente, em caso de atualização do mesmo
                    os.remove(ezl_settings.MEDIA_ROOT + str(ecm.path))

                    ecm.path = 'GEDs/' + str(task.id) + '/' + file
                    ecm.task = task
                    ecm.is_active = True
                    ecm.alter_user = user

                    ecm.save(update_fields=[
                        'path',
                        'task',
                        'is_active',
                        'alter_user',
                        'alter_date'])

                elif task:
                    ecm = self.model(path='GEDs/' + str(task.id) + '/' + file,
                                     task=task,
                                     is_active=True,
                                     legacy_code=ecm_legacy_code,
                                     system_prefix=LegacySystem.ADVWIN.value,
                                     create_user=user,
                                     alter_user=user
                                     )
                    ecm.save()

                if task and ecm and path:

                    # Deve verificar se o arquivo está contido no diretório de GEDs do Advwin. Pois existem caminhos
                    # de arquivos no banco mas não contém o arquivo no sistema de arquivos
                    try:
                        sftp.stat('Agenda/' + file)
                        is_file = True

                    except:
                        is_file = False

                    if is_file:
                        import_dir = '/opt/files_easy_lawyer/' + 'GEDs/' + str(task.id) + '/'
                        if not os.path.exists(import_dir):
                            os.makedirs(import_dir)

                        print('Importando arquivo ' + file + ' ... ')
                        sftp.get(remote_path, import_dir + file, callback=None)
        sftp.close()


if __name__ == "__main__":
    EcmETL().import_data()
