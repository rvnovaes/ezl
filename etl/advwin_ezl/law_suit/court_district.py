# -*- coding:utf-8 -*-
import datetime
import json
import os

import connections
from connections.db_connection import connect_db
from etl.advwin_ezl import settings


def import_data():
    # apaga registros da tabela court_district - tem que ter cascade mesmo que não existam registros
    # associados em outras tabelas
    # restart identity - reinica o id da tabela
    # engine.execute(text('truncate table court_district restart identity cascade;').execution_options(autocommit=True))

    # pega o diretorio do arquivo __init__.py do diretorio corrente e junta com o 'court_district.json'
    json_file_path = os.path.join(os.path.dirname(__file__), 'court_district.json')
    json_file_path = json_file_path.replace('\\', '/')

    json_file = open(json_file_path, encoding="utf8")

    court_district_dict = json.load(json_file)

    for data in court_district_dict:
        name = str(data['court_district']).replace("'", "''").strip()

        query = "insert into court_district(create_date, name, create_user_id, state_id, is_active) values('{0}', " \
                "'{1}', {2}, {3}, {4})"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name, settings.USER,
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
