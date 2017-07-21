import datetime
import json
import os

from sqlalchemy import text

import connections
from connections.db_connection import connect_db


def import_data():
    # apaga registros da tabela city - tem que ter cascade mesmo que não existam registros
    # associados em outras tabelas
    # restart identity - reinica o id da tabela
    engine.execute(text('truncate table city restart identity cascade;').execution_options(autocommit=True))

    # pega o diretorio do arquivo __init__.py do diretorio corrente e junta com o 'state_city.json'
    json_file_path = os.path.join(os.path.dirname(__file__), 'state_city.json')
    json_file_path = json_file_path.replace('\\', '/')

    json_file = open(json_file_path, encoding="utf8")

    city_dict = json.load(json_file)

    for data in city_dict:
        city_name = str(data['name']).replace("'", "''")

        # todo: ainda nao existe uma lista com a comarca (court_district_id) de cada cidade
        query = "insert into city(create_date, name, create_user_id, state_id, is_active) " \
                "values('{0}', '{1}', {2}, {3}, {4})"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    city_name,
                    '1',
                    "(select id from state where name = '" + data['state_name'] + "')",
                    True)

        connection = engine.connect()
        result = connection.execute(query)

        connection.close()

if __name__ == "__main__":
    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'ezl.cfg'
    cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'ezl_local.cfg')

    engine = connect_db(cfg_file)

    import_data()
