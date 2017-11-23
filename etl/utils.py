from os.path import join
from config.config import get_parser


def ecm_path_advwin2ezl(advwin_path):
    part = advwin_path.split('Agenda\\', 1)[1].replace('\\', '/')
    return join('ECM', part)


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
            """.format(model, rows_count, str(error), str(time))
    return msg

def save_error_log(log, create_user, message_error):
    if log:
        log.errors.create(create_user=create_user, error=message_error)
