# ordem de importação
# factory
# user
# country
# state
# court_district
# city
# court_division
# person
# folder
# instance
# law_suit
# type_movement
# type_task
# movement
# task
import os

from django.contrib.auth.models import User
from sqlalchemy import text

import connections
from connections.db_connection import connect_db
from core.utils import LegacySystem
from etl.advwin_ezl import settings
import logging
import datetime


class GenericETL(object):
    advwin_cfg_file = os.path.join(os.path.abspath(os.path.dirname(connections.__file__)), 'advwin_ho.cfg')
    advwin_engine = connect_db(advwin_cfg_file)
    model = None
    import_query = None
    export_query_set = None
    advwin_table = None
    has_status = None
    advwin_model = None
    debug_logger=logging.getLogger('debug_logger')
    error_logger=logging.getLogger('error_logger')
    timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    class Meta:
        abstract = True

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
    def deactivate_records(self):
        if not settings.TRUNCATE_ALL_TABLES:
            records = self.model.objects.filter(system_prefix=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()

    def deactivate_all(self):
        if not settings.TRUNCATE_ALL_TABLES:
            self.model.objects.all().update(is_active=False)

    def config_import(self, rows, user, rows_count):
        pass

    def import_data(self):
        if self.has_status:
            self.deactivate_all()

        connection = self.advwin_engine.connect()

        cursor = self.advwin_engine.execute(text(self.import_query))
        rows = cursor.fetchall()
        rows_count = len(rows)
        user = User.objects.get(pk=settings.USER)

        self.config_import(rows, user, rows_count)

        connection.close()

    def config_export(self):
        pass

    # método para tratar o retorno da query de exportação
    def post_export_handler(self, result):
        pass

    def export_data(self):
        self.config_export()
        connection = self.advwin_engine.connect()

        for query in self.export_query_set:
            trans = connection.begin()
            try:
                result = self.advwin_engine.execute(text(query))
                self.post_export_handler(result)
                trans.commit()
            except:
                trans.rollback()
                raise
        connection.close()
