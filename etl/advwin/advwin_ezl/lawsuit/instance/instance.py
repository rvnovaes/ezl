import os
from datetime import timezone

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

import connections
from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import select_user, truncate_tables
from etl.advwin.models import Base
from connections.db_connection import connect_db
from lawsuit.models import Instance
from django.utils import timezone


def import_data():
    truncate_tables([Instance])
    query = "select Codigo, Descicao from Jurid_Instancia as i1 WHERE Codigo = " \
            "(select min (Codigo) from Jurid_Instancia as i2 WHERE i1.Descicao = i2.Descicao)"

    connection = advwin_engine.connect()
    rows = connection.execute(text(query))
    user = select_user()

    for row in rows:
        instances = Instance.objects.filter(legacy_code=row['Codigo'], system_prefix=LegacySystem.ADVWIN.value).first()

        if instances:
            obj = Instance(
                id=instances.id,
                name=row['Descicao'],
                is_active=True,
                alter_user=user,
                create_date=instances.create_date,
                create_user_id=instances.create_user_id,
                legacy_code=instances.legacy_code,
                system_prefix=instances.system_prefix,
            )

        else:
            obj = Instance(
                name=row['Descicao'],
                is_active=True,
                legacy_code=row['Codigo'],
                alter_user=user,
                create_user=user,
                system_prefix=LegacySystem.ADVWIN.value,
                create_date=timezone.now()

            )

        obj.save()

    connection.close()


if __name__ == "__main__":
    # pega o diretorio do arquivo __init__.py de acordo com o pacote e junta com o 'advwin.cfg'
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')

    advwin_engine = connect_db(advwin_cfg_file)

    import_data()
