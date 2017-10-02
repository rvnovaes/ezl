# esse import deve vir antes de todos porque ele executa o __init__.py
import os
import sys
import ntpath
import paramiko
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from task.models import Ecm
from task.models import Task
from config.config import get_parser
config_parser = get_parser()

try:
    source = dict(config_parser.items('etl'))
    create_user = source['user']
    host_sftp = source['host_sftp']
    port_sftp = source['port_sftp']
    username_sftp = source['username_sftp']
    password_sftp = source['password_sftp']
    local_path = source['local_path']
except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)


class EcmETL(GenericETL):
    import_query = """
                    SELECT
                      G.ID_doc,
                      A.Ident,
                      G.Link
                    FROM Jurid_Ged_Main AS G
                          INNER JOIN Jurid_agenda_table AS A
                            ON G.Codigo_OR = CAST(A.Ident AS VARCHAR(255))
                          INNER JOIN Jurid_Pastas AS P
                            ON A.Pasta = P.Codigo_Comp
                          INNER JOIN Jurid_CodMov AS cm
                            ON A.CodMov = cm.Codigo
                    WHERE G.Tabela_OR = 'Agenda' AND P.Status = 'Ativa' AND G.Link <> '' AND G.Link IS NOT NULL
                          AND cm.UsarOS = 1 AND
                          (p.Status = 'Ativa' OR p.Dt_Saida IS NULL) AND
                          ((a.prazo_lido = 0 AND a.SubStatus = 30) OR (a.SubStatus = 80 AND a.Status = 0))    
                    """

    model = Ecm
    advwin_table = 'Jurid_Ged_Main'
    has_status = False

    def config_import(self, rows, user, rows_count):
        remote_path = ''
        for row in rows:
            print('Registros restantes: ' + str(rows_count))
            rows_count -= 1
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
                file = ntpath.basename(path)
                ecm_legacy_code = row['ID_doc']
                task_legacy_code = row['Ident']

                # Um GED criado no EZL (sem legacy_code) e que já constado no Advwin, neste arquivo será lançado
                # um erro ao tentar adicionar os dados no arquivo no banco de dados, pois os Patchs seriam identicos.
                # Assim, só adiciona um novo registro caso não haja outro como o mesmo Patch
                task = Task.objects.filter(legacy_code=task_legacy_code)
                print('legacy_code' + str(task_legacy_code))
                if task:
                    id_task = task[0].id
                    is_ecm = False
                    if self.model.objects.filter(path='GEDs/' + str(id_task) + '/' + file):
                        is_ecm = True

                    task = Task.objects.filter(legacy_code=task_legacy_code).first()
                    ecm = self.model.objects.filter(legacy_code=ecm_legacy_code, task=task,
                                                    system_prefix=LegacySystem.ADVWIN.value).first() if task else None
                    if task and not is_ecm:
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
                            transport = paramiko.Transport((host_sftp, int(port_sftp)))
                            transport.connect(username=username_sftp, password=password_sftp)
                            sftp = paramiko.SFTPClient.from_transport(transport)
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
                                import_dir = local_path + str(task.id) + '/'

                                # Se não houver nenhum diretório com o ID da task, cria um novo
                                if not os.path.exists(import_dir):
                                    os.makedirs(import_dir)

                                print('Importando arquivo ' + file + ' ... ')
                                sftp.get(remote_path, import_dir + file, callback=None)
                            sftp.close()
                        except:
                            print('Erro de conexao com servidor sftp')


if __name__ == "__main__":
    EcmETL().import_data()
