import datetime
import os

import connections

from sqlalchemy import text

from connections.db_connection import connect_db
from core.utils import LegacySystem
from etl.advwin import settings


def import_data():
    # apaga registros da tabela type_task - tem que ter cascade mesmo que não existam registros
    # associados em outras tabelas
    # restart identity - reinica o id da tabela
    if settings.TRUNCATE_ALL_TABLES:
        ezl_engine.execute(text('truncate table type_task restart identity cascade;').execution_options(
            autocommit=True))

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
    ezl_engine.execute(text("update type_task set is_active = False where legacy_code = '{0}'"
                            .format(LegacySystem.ADVWIN.value)).execution_options(autocommit=True))

    # seleciona os serviços do advwin
    query = "select distinct " \
            "codigo, descricao " \
            "from Jurid_CodMov " \
            "where " \
            "descricao is not null and " \
            "status = 'Ativo' and " \
            "usaros = 1"

    connection = advwin_engine.connect()
    result = connection.execute(query)

    for row in result:
        code = row['codigo']
        name = str(row['descricao']).replace("'", "''")

        query = "select id " \
                "from type_task " \
                "where " \
                "system_prefix = '{0}' and " \
                "legacy_code = '{1}'".format(LegacySystem.ADVWIN.value, code)

        connection = ezl_engine.connect()
        result = connection.execute(query)

        if result.rowcount > 0:
            for r in result:
                query = "update type_task set " \
                        "alter_date = '{0}', " \
                        "is_active = {1}, " \
                        "name = '{2}', " \
                        "alter_user_id = {3} " \
                        "where id = {4}" \
                    .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            True, name, settings.USER, r['id'])
        else:
            query = "insert into type_task(create_date, is_active, legacy_code, name, create_user_id, " \
                    "system_prefix) values('{0}', {1}, '{2}', '{3}', {4}, '{5}')" \
                .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        True,
                        code,
                        name, settings.USER,
                        LegacySystem.ADVWIN.value)

        connection = ezl_engine.connect()
        result = connection.execute(query)

    connection.close()


if __name__ == "__main__":
    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'advwin.cfg'
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')

    advwin_engine = connect_db(advwin_cfg_file)

    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'ezl.cfg'
    ezl_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'ezl_local.cfg')

    ezl_engine = connect_db(ezl_cfg_file)

    import_data()
