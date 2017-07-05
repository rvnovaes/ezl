import os

from sqlalchemy import text

import connections
from connections.db_connection import connect_db
from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import truncate_tables, deactivate_records, select_user
from lawsuit.models import CourtDivision


def import_data():
    truncate_tables([CourtDivision])
    deactivate_records([CourtDivision])

    # seleciona codigo e descricao das varas com descricao (distinct) do advwin
    query = "select codigo, descricao from Jurid_Varas as v1 " \
            "where codigo = (select min(codigo) from Jurid_Varas as v2 where v1.descricao = v2.descricao)"

    connection = advwin_engine.connect()
    rows = connection.execute(text(query))
    user = select_user()

    for row in rows:
        code = (str(row['codigo'])).strip()
        name = (str(row['descricao']).replace("'", "''")).strip()

        # tem que verificar se é novo antes para não salvar o create_user ao fazer update
        court_divisions = CourtDivision.objects.filter(legacy_code=code, system_prefix=LegacySystem.ADVWIN.value)
        if court_divisions:
            for court_division in court_divisions:
                obj = CourtDivision(id=court_division.id,
                                    name=name,
                                    is_active=True,
                                    alter_user=user)
        else:
            obj = CourtDivision(name=name,
                                is_active=True,
                                legacy_code=code,
                                system_prefix=LegacySystem.ADVWIN.value,
                                create_user=user,
                                alter_user=user)
        obj.save()

    connection.close()


if __name__ == "__main__":
    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'advwin.cfg'
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')

    advwin_engine = connect_db(advwin_cfg_file)

    import_data()
