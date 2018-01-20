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
import time
from functools import wraps, reduce

from sqlalchemy import text
from connections.db_connection import connect_db, get_advwin_engine
from core.utils import LegacySystem
from config.config import get_parser
from etl.models import DashboardETL
from django.utils import timezone


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = get_parser()

try:
    source = dict(parser.items('etl'))
    truncate_all_tables = source['truncate_all_tables']
    create_alter_user = source['user']
    config_connection = source['connection_name']
    source_etl_connection = dict(parser.items(source['connection_name']))
    db_name_source = source_etl_connection['database']
    db_host_source = source_etl_connection['server']
except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)


def validate_import(f):
    """
    Funcao responvavel por validar os dados importados do ADVWin
    Ela demonstra atraves do log a quantidade de registros lidos, quantidade de registros salvos,
    quantidade
    registros nao salvos, e os registros que nao foram salvos.
    Para utitilizar este metodo basta decorar a funcao config_import.
    E necessario tambem a existem do atributo model, e field_check na classe.
         - model e o modelo onde sera importado os dados no ezl
         - field_check e o atributo do modelo onde sera checado as importacoes realizadas
           Por padrao o field_check sera legacy_code, caso tenha a necessidade de ser um atributo
           diferente
           este devera ser sobrescrito pela classe filha de GenericETL
           Na a query atribuida ao atributo import_query devera conter pelomenos o mesmo campo que
           definido no
           field_check, exemplo 'SELECT pm.Ident AS legacy_code...' (--> o alias do campo a ser
           checado deve ser o mesmo defindo em check_field)
    :param f:
    :type: func
    :return f:
    """

    @wraps(f)
    def wrapper(etl, rows, user, rows_count, log, *args, **kwargs):
        res = f(etl, rows, user, rows_count, *args, **kwargs)
        debug_logger = etl.debug_logger
        error_logger = etl.error_logger
        name_class = etl.model._meta.verbose_name
        try:
            field_check = etl.field_check
            advwin_values = [str(i[field_check]) for i in rows]

            params = {'{}__in'.format(etl.EZL_LEGACY_CODE_FIELD): advwin_values}
            qset = etl.model.objects.filter(**params)

            parts = etl.EZL_LEGACY_CODE_FIELD.split('__')
            chain = parts[:-1]
            related = '__'.join(chain)
            if related:
                qset = qset.select_related(related)

            for entry in qset:
                debug_logger.debug('{}: REGISTROSALVO - {}'.format(name_class, entry))

            ezl_values = [reduce(getattr, parts, entry) for entry in qset]

            read_quantity = len(advwin_values)
            written_amount = len(ezl_values)

            not_imported = set(advwin_values) - set(ezl_values)

            debug_logger.debug(name_class + ' - Quantidade lida:  {0}'.format(read_quantity))
            debug_logger.debug(name_class + ' - Quantidade salva: {0}'.format(written_amount))
            debug_logger.debug(
                name_class + ' - Quantidade nao importada {0}'.format(len(not_imported)))
            if not_imported:
                error_logger.error(
                    name_class + ' - Quantidade nao importada {0}'.format(len(not_imported)))
                error_logger.error(
                    name_class + ' -  Registros nao importadados {0}'.format(str(not_imported)))
            log.imported_quantity = written_amount
            log.save()
            return res
        except Exception as exc:
            error_logger.error(etl.model._meta.verbose_name + ': Nao foi possivel validar ')
            error_logger.error(exc)

    return wrapper


class GenericETL(object):
    EZL_LEGACY_CODE_FIELD = 'legacy_code'
    model = None
    import_query = None
    export_statements = None
    advwin_table = None
    has_status = None
    advwin_model = None
    debug_logger = logging.getLogger('debug_logger')
    error_logger = logging.getLogger('error_logger')
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    field_check = 'legacy_code'

    class Meta:
        abstract = True

    # inativa todos os registros já existentes para não ter que consultar ativos e inativos do
    # legado
    def deactivate_records(self):
        if not truncate_all_tables:
            records = self.model.objects.filter(system_prefix=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()

    def deactivate_all(self):
        if not truncate_all_tables:
            self.model.objects.all().update(is_active=False)

    def config_import(self, rows, user, rows_count, log=False):
        raise NotImplementedError()

    def import_data(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=create_alter_user)
        dashboard_log = DashboardETL.objects.create(
            name=self.model._meta.verbose_name.upper(), status=False,
            executed_query=self.import_query, create_user=user,
            db_name_source=db_name_source, db_host_source=db_host_source)
        if self.has_status:
            self.deactivate_all()

        for attempt in range(5):
            try:
                connection = get_advwin_engine().connect()
                cursor = connection.execute(text(self.import_query))
                rows = cursor.fetchall()
                rows_count = len(rows)
                user = User.objects.get(pk=create_alter_user)
                self.config_import(rows, user, rows_count, log=dashboard_log)
                dashboard_log.execution_date_finish = timezone.now()
                dashboard_log.read_quantity = rows_count
                dashboard_log.status = True
                dashboard_log.save()
                connection.close()
            except:
                self.error_logger.error("Erro de conexão. Nova tentativa de conexão em 5s. Tentativa: " + str(attempt + 1))
                time.sleep(5)
            else:
                break
        else:
            self.error_logger.error("Não foi possível conectar com o banco.")

    def config_export(self):
        pass

    # método para tratar o retorno da query de exportação
    def post_export_handler(self, result):
        pass

    def export_data(self):
        self.config_export()
        connection = self.advwin_engine().connect()

        for stmt in self.export_statements:
            trans = connection.begin()
            try:
                result = connection.execute(stmt)
                self.post_export_handler(result)
                trans.commit()
            except:
                trans.rollback()
                raise
        connection.close()
