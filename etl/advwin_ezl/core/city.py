import json
import os
import sys
from sqlalchemy import text
import connections
from connections.db_connection import connect_db
import logging
import datetime
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

    debug_logger = logging.getLogger('debug_logger')
    error_logger = logging.getLogger('error_logger')
    timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # apaga registros da tabela city - tem que ter cascade mesmo que não existam registros
        # associados em outras tabelas
        # restart identity - reinica o id da tabela
        engine.execute(
            text('truncate table city restart identity cascade;').
            execution_options(autocommit=True))

        # pega o diretorio do arquivo __init__.py do diretorio corrente e junta com o 'city.json'
        json_file_path = os.path.join(os.path.dirname(__file__), 'city.json')
        json_file_path = json_file_path.replace('\\', '/')

        json_file = open(json_file_path, encoding="utf8")

        city_dict = json.load(json_file)

        for data in city_dict:
            city_name = str(data['name']).replace("'", "''")
            court_district = str(data['court_district']).replace("'", "''")

            query = "SELECT id FROM state WHERE initials = '" + data[
                'state'] + "';"
            connection = engine.connect()
            result = connection.execute(query)
            state_id = ''
            for row in result:
                state_id = str(row['id'])

            if state_id == '':
                print(query)

            # todo: ainda nao existe uma lista com a comarca (court_district_id) de cada cidade
            query = "insert into city(create_date, name, court_district_id, create_user_id, state_id, is_active) " \
                    "values('{0}', '{1}', {2}, {3}, {4}, {5})" \
                .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        city_name,
                        "(select id from court_district where "
                        "name = '" + court_district + "' and state_id = " + state_id + ")",
                        create_user,
                        state_id,
                        True)

            connection = engine.connect()
            result = connection.execute(query)
            connection.close()
            debug_logger.debug(
                "Cidade,%s,%s,%s,%s" % (str(city_name), str(court_district),
                                        str(state_id), timestr))

    except Exception as e:
        error_logger.error("Ocorreu o seguinte erro na importacao de Cidade: "
                           + str(e) + "," + timestr)


if __name__ == "__main__":
    engine = connect_db(config_parser, 'django_application')
    import_data()
