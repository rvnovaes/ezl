from os.path import join
from config.config import get_parser
from core.models import Person


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


def get_users_to_import():
    """Retorna os ids dos correspondentes que devemos importar"""
    return Person.objects.filter(
        auth_user__groups__name=Person.CORRESPONDENT_GROUP).values_list(
            'legacy_code', flat=True)
