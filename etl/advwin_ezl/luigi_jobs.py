import sys
import django
import os

dir = os.path.dirname(os.path.realpath(__file__))
position = dir.find('easy_lawyer_django')
sys.path.append(dir[:position] + 'easy_lawyer_django/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ezl.settings'
django.setup()

import subprocess

from time import sleep

from etl.advwin_ezl import signals
from etl.advwin_ezl.account.user import UserETL
from etl.advwin_ezl.core.person import PersonETL
from etl.advwin_ezl.core.address import AddressETL
from etl.advwin_ezl.core.ContactMechanism import ContactMechanismETL
from etl.advwin_ezl.factory import InvalidObjectFactory
from etl.advwin_ezl.law_suit.court_division import CourtDivisionETL
from etl.advwin_ezl.law_suit.folder import FolderETL
from etl.advwin_ezl.law_suit.instance import InstanceETL
from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
from etl.advwin_ezl.law_suit.movement import MovementETL
from etl.advwin_ezl.law_suit.type_movement import TypeMovementETL
from etl.advwin_ezl.task.task import TaskETL
from etl.advwin_ezl.task.type_task import TypeTaskETL
from etl.advwin_ezl.task.ged_task import EcmETL
from django.core.management import call_command
from django.core.management.commands import loaddata, migrate
import luigi
from luigi.interface import core
from ezl import settings
from etl.advwin_ezl import settings as etl_settings
from etl.advwin_ezl.ezl_exceptions.params_exception import ParamsException

LINUX_PASSWORD = None


# A ordem de inclusão das fixtures é importante, favor não alterar
fixtures = ['country.xml', 'state.xml', 'court_district.xml', 'city.xml', 'type_movement.xml',
            'type_task.xml']


# ipc da funcao get_folder_ipc significa inter process communication
def get_folder_ipc(task):
    return settings.BASE_DIR + '/etl/advwin_ezl/tmp/%s.ezl' % task.task_id


def load_fixtures():
    for fixture in fixtures:
        call_command(loaddata.Command(), fixture, verbosity=0)


def load_luigi_scheduler():
    if subprocess.run(['pgrep', '-f', 'luigid'], stdout=subprocess.PIPE).stdout.decode("utf-8") is '':
        command = 'echo {0}|sudo -S luigid --port {1} --background'.format(
            LINUX_PASSWORD, etl_settings.LUIGI_PORT)
        os.system(command)
        # tempo necessário para inicialização do luigi scheduler antes da primeira tarefa NAO REMOVER
        sleep(2)


class MigrationTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def run(self):
        # Injeção de contexto (Carrega modulo do signals)
        signals
        call_command(migrate.Command(), verbosity=0)
        print('Migration finalizada...')
        f = open(get_folder_ipc(self),
                 'w')
        f.close()


# task inicial
class ConfigTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield MigrationTask()

    def run(self):
        signals
        # call_command(migrate.Command(), verbosity=0)
        # sleep(5)
        InvalidObjectFactory().restart_table_id()
        InvalidObjectFactory.create()
        load_fixtures()
        print('Configuração inicial finalizada...')
        f = open(get_folder_ipc(self),
                 'w')
        f.close()


class UserTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield ConfigTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        UserETL().import_data()


class CourtDivisionTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield UserTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        CourtDivisionETL().import_data()


class InstanceTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield CourtDivisionTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        InstanceETL().import_data()


class PersonTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield InstanceTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        PersonETL().import_data()


class AddressTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield PersonTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        AddressETL().import_data()


class ContactMechanismTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield PersonTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        ContactMechanismETL().import_data()


class FolderTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield AddressTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        FolderETL().import_data()


class LawsuitTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield FolderTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        LawsuitETL().import_data()


class TypeMovementTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield LawsuitTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        TypeMovementETL().import_data()


class TypeTaskTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield TypeMovementTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        TypeTaskETL().import_data()


class MovementTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield TypeTaskTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        MovementETL().import_data()


class TaskTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield MovementTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        TaskETL().import_data()


class EcmTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield TaskTask()

    def run(self):
        f = open(get_folder_ipc(self), 'w')
        f.close()
        EcmETL().import_data()


if __name__ == "__main__":
    try:
        args = dict(map(lambda x: x.lstrip('-').split('='), sys.argv[1:]))
        if 'p' not in args.keys():
            raise ParamsException
        sys.argv.pop(1)
        # E necessario remover os arquivos.ezl dentro do diretorio tmp para executar novamente
        LINUX_PASSWORD = args.get('p')
        os.system('echo {0}|sudo -S rm -rf {1}/etl/advwin_ezl/tmp/*.ezl'.format(
            LINUX_PASSWORD, settings.BASE_DIR))
        # Importante ser a ultima tarefa a ser executada pois ela vai executar todas as dependencias
        load_luigi_scheduler()
        luigi.run(main_task_cls=EcmTask())
    except ParamsException as e:
        print(e)
    except Exception as e:
        print(e)