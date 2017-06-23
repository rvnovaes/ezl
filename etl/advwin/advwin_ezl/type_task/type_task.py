import datetime
import json
import os

import connections

from sqlalchemy import text

from connections.db_connection import connect_db


def import_data():
    # apaga registros da tabela type_task - tem que ter cascade mesmo que não existam registros
    # associados em outras tabelas
    # restart identity - reinica o id da tabela
    engine.execute(text('truncate table type_task restart identity cascade;').execution_options(autocommit=True))

    # seleciona os serviços do advwin
    query = "select * from Jurid_ProcMov where table_schema not in " \
            "('information_schema','pg_catalog') and COLUMN_NAME = 'court_district_id'"

    connection = engine.connect()
    result = connection.execute(query)

    for row in result:
        try:
            # limpa dependencia da fk court_district_id
            engine.execute(text('update ' + row['table_name'] + ' set court_district_id = null;').
                           execution_options(autocommit=True))
        except exc.IntegrityError:
            pass

    # pega o diretorio do arquivo __init__.py do diretorio corrente e junta com o 'state_court_district.json'
    json_file_path = os.path.join(os.path.dirname(__file__), 'state_court_district.json')
    json_file_path = json_file_path.replace('\\', '/')

    json_file = open(json_file_path, encoding="utf8")

    court_district_dict = json.load(json_file)

    for data in court_district_dict:
        court_district_name = str(data['court_district']).replace("'", "''")

        query = "insert into court_district(create_date, name, create_user_id, state_id, is_active) values('{0}', " \
                "'{1}', {2}, {3}, {4})"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    court_district_name, '1',
                    "(select id from state where initials = '" + data['state'] + "')",
                    True)

        connection = engine.connect()
        result = connection.execute(query)

    connection.close()

if __name__ == "__main__":
    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'ezl.cfg'
    cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'ezl_local.cfg')

    engine = connect_db(cfg_file)

    import_data()
