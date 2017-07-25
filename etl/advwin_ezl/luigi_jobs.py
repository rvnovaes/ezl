import os
import subprocess
import sys
from time import sleep

import django

from etl.advwin_ezl import signals
from etl.advwin_ezl.account.user import UserETL
from etl.advwin_ezl.core.person import PersonETL
from etl.advwin_ezl.factory import InvalidObjectFactory
from etl.advwin_ezl.law_suit.court_division import CourtDivisionETL
from etl.advwin_ezl.law_suit.folder import FolderETL
from etl.advwin_ezl.law_suit.instance import InstanceETL
from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
from etl.advwin_ezl.law_suit.movement import MovementETL
from etl.advwin_ezl.law_suit.type_movement import TypeMovementETL
from etl.advwin_ezl.task.task import TaskETL
from etl.advwin_ezl.task.type_task import TypeTaskETL
from ezl import settings

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()
from django.core.management import call_command
from django.core.management.commands import loaddata, migrate
import luigi

# A ordem de inclusão das fixtures é importante, favor não alterar
fixtures = ['country.xml', 'state.xml', 'court_district.xml']


def get_folder_ipc(task):
    return settings.BASE_DIR + '/etl/advwin_ezl/tmp/%s.ezl' % task.task_id


def load_fixtures():
    for fixture in fixtures:
        call_command(loaddata.Command(), fixture, verbosity=0)


def load_luigi_scheduler():
    if subprocess.run(['pgrep', '-f', 'luigid'], stdout=subprocess.PIPE).stdout.decode("utf-8") is '':
        os.system('echo %s|sudo -S %s %s' % ('123456', 'luigid', '--background'))
        # tempo necessário para inicialização do luigi scheduler antes da primeira tarefa NAO REMOVER
        sleep(1)


# task inicial
class ConfigTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def run(self):
        signals
        call_command(migrate.Command(), verbosity=0)
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


class FolderTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(
            path=get_folder_ipc(self))

    def requires(self):
        yield PersonTask()

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
        yield LawsuitETL()

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


if __name__ == "__main__":
    load_luigi_scheduler()
    luigi.run(main_task_cls=TaskTask())
    dir = settings.BASE_DIR + '/etl/advwin_ezl/tmp/'  # luigi.run(main_task_cls=UserTask())
    os.system('echo %s|sudo -S rm -rf %s*.ezl' % ('123456', dir))
    # os.system('sudo kill $(pgrep -f luigid)',)
    # os.system('echo %s'%'123')
    # '| sudo kill $(pgrep -f luigid)' % '123456')
