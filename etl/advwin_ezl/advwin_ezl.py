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
import sys
import logging
import datetime
from functools import wraps
import configparser
from django.contrib.auth.models import User
from sqlalchemy import text

import connections
from connections.db_connection import connect_db
from core.utils import LegacySystem


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = configparser.ConfigParser()

try:
    with open(os.path.join(BASE_DIR, 'config', 'general.ini')) as config_file:
        parser.read_file(config_file)
        source = dict(parser.items('etl'))
        truncate_all_tables = source['truncate_all_tables']
        create_alter_user = source['user']

except FileNotFoundError:
    print('OOOOOOOOOOOOOOOOOOOOOOOOOOOHHHHH NOOOOOOOO!!!!!')
    print('general.ini file was not found on {config_path}'.format(config_path=os.path.join(BASE_DIR, 'config')))
    print('Rename it to general.ini and specify the correct configuration settings!')
    sys.exit(0)


def validate_import(f):
    """
    Funcao responvavel por validar os dados importados do ADVWin
    Ela demonstra atraves do log a quantidade de registros lidos, quantidade de registros salvos, quantidade
    registros nao salvos, e os registros que nao foram salvos.
    Para utitilizar este metodo basta decorar a funcao config_import.
    E necessario tambem a existem do atributo model, e field_check na classe.
         - model e o modelo onde sera importado os dados no ezl
         - field_check e o atributo do modelo onde sera checado as importacoes realizadas
           Por padrao o field_check sera legacy_code, caso tenha a necessidade de ser um atributo diferente
           este devera ser sobrescrito pela classe filha de GenericETL
           Na a query atribuida ao atributo import_query devera conter pelomenos o mesmo campo que definido no
           field_check, exemplo "SELECT pm.Ident AS legacy_code..." (--> o alias do campo a ser
           checado deve ser o mesmo defindo em check_field)
    :param f:
    :type: func
    :return f:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        debug_logger = args[0].debug_logger
        error_logger = args[0].error_logger
        name_class = args[0].model._meta.verbose_name
        try:
            field_check = args[0].field_check
            advwin_values = list(map(lambda i: str(i[field_check]), args[1]))
            filter_ezl = 'args[0].model.objects.filter({0}__in={1})'.format(field_check, advwin_values)
            ezl_imported_values = eval(filter_ezl)
            list(map(lambda i: debug_logger.debug(name_class + ': REGISTRO SALVO - ' + str(i.__dict__)),
                     ezl_imported_values))
            ezl_values = list(map(lambda i: eval('i.' + field_check), ezl_imported_values))
            read_quantity = len(advwin_values)
            written_amount = len(ezl_values)
            not_imported = set(advwin_values) - set(ezl_values)
            debug_logger.debug(name_class + ' - Quantidade lida:  {0}'.format(read_quantity))
            debug_logger.debug(name_class + ' - Quantidade salva: {0}'.format(written_amount))
            debug_logger.debug(name_class + ' - Quantidade nao importada {0}'.format(len(not_imported)))
            if not_imported:
                error_logger.error(name_class + ' - Quantidade nao importada {0}'.format(len(not_imported)))
                error_logger.error(name_class + ' -  Registros nao importadados {0}'.format(str(not_imported)))
            return res
        except:
            error_logger.error(args[0].model._meta.verbose_name + ': Nao foi possivel validar ')
            pass
    return wrapper


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

    field_check = 'legacy_code'

    class Meta:
        abstract = True

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
    def deactivate_records(self):
        if not truncate_all_tables:
            records = self.model.objects.filter(system_prefix=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()

    def deactivate_all(self):
        if not truncate_all_tables:
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
        user = User.objects.get(pk=create_alter_user)

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
