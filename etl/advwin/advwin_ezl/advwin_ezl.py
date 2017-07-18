# ordem de importação
# user - inserir id do usuário configurado em etl/advwin/settings.py
# country
# state
# court_district
# city
# court_division
# person
# folder
# instance
# law_suit
# movement
# task
# todo: acho que tem que ser feito um script que roda todos os scripts de etl na ordem correta pra não dar erro de fk
# todo: ou pode ser usado o luigi com o crontab
import os

from django.contrib.auth.models import User
from sqlalchemy import text

import connections
from connections.db_connection import connect_db
from core.utils import LegacySystem
from etl.advwin import settings as etl_settings


class GenericETL(object):
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')
    advwin_engine = connect_db(advwin_cfg_file)
    model = None
    query = None
    advwin_table = None
    has_status = None

    class Meta:
        abstract = True

    # apaga registros das tabelas
    def truncate_table(self):
        if etl_settings.TRUNCATE_ALL_TABLES:
            self.model.objects.all().delete()

    @staticmethod
    def truncate_tables(table_list):
        if etl_settings.TRUNCATE_ALL_TABLES:
            for table in table_list:
                table.objects.all().delete()

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
    def deactivate_records(self):
        if not etl_settings.TRUNCATE_ALL_TABLES:
            records = self.model.objects.filter(system_prefix=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()

    def load_etl(self, rows, user, rows_count):
        pass

    def import_data(self):
        self.truncate_table()
        if self.has_status:
            self.deactivate_records()

        connection = self.advwin_engine.connect()

        cursor = self.advwin_engine.execute(text(self.query))
        rows = cursor.fetchall()
        rows_count = len(rows)
        user = User.objects.get(pk=etl_settings.USER)

        self.load_etl(rows, user, rows_count)

        connection.close()
