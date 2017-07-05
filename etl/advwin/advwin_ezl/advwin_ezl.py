# ordem de importação
# user - inserir id do usuário configurado em etl/advwin/settings.py
# state
# court_district
# city
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

    class Meta:
        abstract = True

    # apaga registros das tabelas
    # tem que ter cascade mesmo que não existam registros associados em outras tabelas
    # restart identity - reinica o id da tabela
    def truncate_table(self):
        if etl_settings.TRUNCATE_ALL_TABLES:
            self.model.objects.all().delete()

    # def has_status_column(self):
    #     if self.advwin_table:
    #         connection = self.advwin_engine.connect()
    #         query = "SELECT DISTINCT SYSOBJECTS.NAME " \
    #                 " FROM SYSCOLUMNS INNER JOIN SYSOBJECTS ON SYSCOLUMNS.ID = SYSOBJECTS.ID" \
    #                 " WHERE SYSCOLUMNS.NAME = 'status' AND SYSOBJECTS.NAME =" \
    #                 + self.advwin_table + " AND SYSOBJECTS.XTYPE = 'U' ORDER BY SYSOBJECTS.NAME"
    #         rows = connection.execute(text(query))
    #         return rows

    @staticmethod
    def truncate_tables(table_list):
        if etl_settings.TRUNCATE_ALL_TABLES:
            for table in table_list:
                table.objects.all().delete()

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
    def deactivate_records(self):
        if not etl_settings.TRUNCATE_ALL_TABLES:
            records = self.model.objects.filter(legacy_code=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()

    def load_etl(self, rows, user):
        pass

    def import_data(self):

        self.truncate_table()
        # if self.has_status_column():
        #     self.deactivate_records()

        connection = self.advwin_engine.connect()

        rows = connection.execute(text(self.query))
        user = User.objects.get(pk=etl_settings.USER)

        self.load_etl(rows, user)

        connection.close()
