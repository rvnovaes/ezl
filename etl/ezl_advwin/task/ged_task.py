import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
# import django
# django.setup()

from datetime import datetime
from etl.advwin_ezl import settings
from pathlib import Path
import paramiko
from sqlalchemy import text
import connections
from connections.db_connection import connect_db
from task.models import Ecm


class EcmETL:
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')
    advwin_engine = connect_db(advwin_cfg_file)
    model = Ecm
    query = None
    advwin_table = None
    has_status = None

    def extract_data(self):
        return self.model.objects.filter(updated=True)

    def export_data(self):
        connection = self.advwin_engine.connect()
        ecms = self.extract_data()

        transport = paramiko.Transport((settings.host_sftp, settings.port_sftp))
        transport.connect(username=settings.username_sftp, password=settings.password_sftp)
        sftp = paramiko.SFTPClient.from_transport(transport)

        for ecm in ecms:

            # Nome das variáveis de acordo com as colunas do Advwin
            nome = ecm.filename
            tabela_or = 'Agenda'
            codigo_OR = ecm.task.legacy_code
            id_OR = 0
            link = '\\' + "\\172.27.155.11\ged_advwin$\Agenda\\" + str(codigo_OR) + "\\" + nome + ""
            # data = '2015-09-30 09:08:18.580'
            data = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            arq_tipo = os.path.splitext(str(ecm.path))[1][1:]
            responsavel = settings.create_user
            arq_status = 'Guardado'
            arq_versao = 1

            insert_query = "INSERT INTO Jurid_Ged_Main (Tabela_OR, Codigo_OR, Id_OR, Descricao, Link, Data, Nome, " \
                           "Responsavel, Unidade, Seguranca, Arquivo, Arq_tipo, Arq_Versao, Arq_Status, Arq_usuario, " \
                           "Arq_nick, Data_morto, PagIni, PagFim, Texto, Obs, chaveSync, id_pasta)" \
                           " VALUES(" \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           "NULL, NULL, NULL, " \
                           "'%s'," \
                           "'%s'," \
                           "'%s'," \
                           " NULL," \
                           "'%s'," \
                           " NULL, NULL," \
                           " NULL, NULL, NULL, NULL, NULL )" \
                           % (
                               tabela_or, codigo_OR, id_OR, nome, link, data, nome, responsavel, arq_tipo,
                               arq_versao,
                               arq_status, nome)

            local_path = os.path.join(settings.local_path, str(ecm.task_id), nome)
            # Verifica se o arquivo está no sistema de arquivos para ser copiado ao servidor de arquivos Advwin

            print('Path: ' + local_path)
            if Path(local_path).is_file():
                is_file = True

            else:
                is_file = False
                print('nenhum arquivo encontrado')

            if is_file:
                cursor = self.advwin_engine.execute(text(insert_query))

                if cursor:

                    # Verifica tenta verificar se no servidor Advwin, possui um diretório com o Legacy Code da providência
                    # Caso não tenha, cria o diretório para inserir o(s) GED(s)
                    try:
                        sftp.stat('Agenda\\' + str(codigo_OR) + '\\')

                    except:
                        sftp.mkdir('Agenda\\' + str(codigo_OR))

                    sftp.put(local_path, 'Agenda\\' + str(codigo_OR) + '\\' + str(nome))

                    ecm.updated = False
                    ecm.save(update_fields=['updated'])

                    # Recupera o ID_doc do novo GED para inserir na tabela Jurid_Ged_Hist
                    id_doc_query = "SELECT ID_doc FROM Jurid_Ged_Main WHERE Link LIKE '%s' AND Codigo_OR = '%s'" % \
                                   ("%" + nome + "%", ecm.task.legacy_code)

                    cursor = self.advwin_engine.execute(text(id_doc_query))
                    row = cursor.fetchone()
                    id_doc = row['ID_doc']

                    # Inserção na tabela Jurid_Ged_Hist
                    insert_ged_hist = "INSERT INTO Jurid_Ged_Hist " \
                                      "(Id_doc, Data_hist, Hist_versao, Hist_link, Hist_Nick, Hist_usuario)" \
                                      " VALUES ('%s','%s','%s','%s','%s','%s')" % (
                                          id_doc, data, 1, link, nome, responsavel)
                    cursor = self.advwin_engine.execute(text(insert_ged_hist))

                    if cursor:
                        print('GED Exportado com sucesso')

                    else:
                        print('Erro na exportação do GED')
                else:
                    print('Erro no Insert no banco Advwin')
            else:
                print('Arquivo local não encontrado')

        if not ecms:
            print('Nenhum GED a ser exportados')

        connection.close()
        sftp.close()


if __name__ == "__main__":
    EcmETL().export_data()
