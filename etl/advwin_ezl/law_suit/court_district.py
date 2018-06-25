# -*- coding:utf-8 -*-
import datetime
import json
import os
import sys
from connections.db_connection import connect_db
from config.config import get_parser
config_parser = get_parser()
try:
    source = dict(config_parser.items('etl'))
    create_user = source['user']
except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)


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
                    name, create_user,
                    "(select id from state where initials = '" + data['state'] + "')",
                    True)

        connection = engine.connect()
        result = connection.execute(query)

    connection.close()

if __name__ == "__main__":
    engine = connect_db(config_parser, 'django_application')

    import_data()
