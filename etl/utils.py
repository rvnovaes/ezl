from os.path import join
from config.config import get_parser
from core.models import Person
import logging
import traceback

ERROR_LOGGER = logging.getLogger('error_logger')
ECM_PATH_ADVWIN2EZL = 'ERRO ao converter o path do ECM - {e}'

def ecm_path_advwin2ezl(advwin_path):
    try:
        if '\\Pastas\\' in advwin_path:
            part = advwin_path.split('Pastas\\', 1)[1].replace('\\', '/')
            return join('ECM', 'Pastas', part)
        else:
            part = advwin_path.split('Agenda\\', 1)[1].replace('\\', '/')
            return join('ECM', part)
    except IndexError as e:
        ERROR_LOGGER.error(ECM_PATH_ADVWIN2EZL.format(e=e))
        ERROR_LOGGER.error(traceback.print_tb(e.__traceback__))
    except Exception as e:
        ERROR_LOGGER.error(ECM_PATH_ADVWIN2EZL.format(e=e))
        ERROR_LOGGER.error(traceback.print_tb(e.__traceback__))


def ecm_path_ezl2advwin(ezl_path):
    """
    O Link deve ser armazenado na seguinte estrutura inicial no advwin:
    \\host\ged_advwin$\Agenda\...
    """
    storage_server = get_parser()['etl']['host_sftp']
    part = ezl_path.split('ECM/', 1)[1]
    path = join('//', storage_server, 'ged_advwin$', 'Agenda', part).replace('/', '\\')
    return path


def get_ecm_file_name(ezl_path):
    return ezl_path.split('/')[-1]


def get_message_log_default(model_name, rows_count, error, time):
    msg = """Ocorreu o seguinte erro na importacao de {0}: {1}, {2}, {3}
            """.format(model_name, rows_count, str(error), str(time))
    return msg


def save_error_log(log, create_user, message_error):
    if log:
        log.errors.create(create_user=create_user, error=message_error)



def get_users_to_import():
    """Retorna os ids dos correspondentes que devemos importar"""
    return Person.objects.filter(
        auth_user__groups__name=Person.CORRESPONDENT_GROUP).values_list(
            'legacy_code', flat=True)


def get_message_log_default(model_name, rows_count, error, time):
    msg = """Ocorreu o seguinte erro na importacao de {0}: {1}, {2}, {3}
            """.format(model_name, rows_count, str(error), str(time))
    return msg

def save_error_log(log, create_user, message_error):
    if log:
        log.errors.create(create_user=create_user, error=message_error)
