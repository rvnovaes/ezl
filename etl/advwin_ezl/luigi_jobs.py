import sys
import os
from datetime import datetime
from etl.advwin_ezl import signals
from etl.advwin_ezl.account.user import UserETL
from etl.advwin_ezl.core.person import PersonETL
from etl.advwin_ezl.core.address import AddressETL
from etl.advwin_ezl.core.contact_mechanism import ContactMechanismETL
from etl.advwin_ezl.law_suit.organ import OrganETL
from etl.advwin_ezl.factory import InvalidObjectFactory, DefaultOffice
from etl.advwin_ezl.financial.cost_center import CostCenterETL
from etl.advwin_ezl.law_suit.court_division import CourtDivisionETL
from etl.advwin_ezl.law_suit.folder import FolderETL
from etl.advwin_ezl.law_suit.instance import InstanceETL
from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
from etl.advwin_ezl.law_suit.movement import MovementETL
from etl.advwin_ezl.law_suit.type_movement import TypeMovementETL
from etl.advwin_ezl.task.task import TaskETL
from etl.advwin_ezl.task.ecm_task import EcmEtl
from django.core.management import call_command
from django.core.management.commands import loaddata, migrate
import luigi
from django.conf import settings
from etl.advwin_ezl.ezl_exceptions.params_exception import ParamsException
from config.config import get_parser
config_parser = get_parser()

try:
    source = dict(config_parser.items('etl'))
    linux_password = source['linux_password']
    luigi_port = source['luigi_port']
except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)


def get_target_path(task):
    return os.path.join(settings.LUIGI_TARGET_PATH,
                        "{}.lock".format(task.task_id))


class MigrationTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def run(self):
        # Injeção de contexto (Carrega modulo do signals)
        signals
        call_command(migrate.Command(), verbosity=0)
        print('Migration finalizada...')
        self.output().open("w").close()


# task inicial
class ConfigTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield MigrationTask(self.date_interval)

    def run(self):
        signals
        # call_command(migrate.Command(), verbosity=0)
        # sleep(5)
        InvalidObjectFactory.create()
        DefaultOffice.create()
        self.output().open("w").close()


class CourtDivisionTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield ConfigTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        CourtDivisionETL().import_data()


class InstanceTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield CourtDivisionTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        InstanceETL().import_data()


class PersonTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield InstanceTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        PersonETL().import_data()


class OrganTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield PersonTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        OrganETL().import_data()


class ContactMechanismTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield OrganTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        ContactMechanismETL().import_data()


class AddressTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield ContactMechanismTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        AddressETL().import_data()


class CostCenterTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield AddressTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        CostCenterETL().import_data()


class FolderTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield CostCenterTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        FolderETL().import_data()


class LawsuitTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield FolderTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        LawsuitETL().import_data()


class TypeMovementTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield LawsuitTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        TypeMovementETL().import_data()


class MovementTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield TypeMovementTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        MovementETL().import_data()


class TaskTask(luigi.Task):
    date_interval = luigi.DateHourParameter()

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield MovementTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        TaskETL().import_data()


class EcmTask(luigi.Task):
    date_interval = luigi.DateHourParameter(default=datetime.now())

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def requires(self):
        yield TaskTask(self.date_interval)

    def run(self):
        self.output().open("w").close()
        EcmEtl().import_data()


class TaskExport(luigi.Task):
    date_interval = luigi.DateHourParameter(default=datetime.now())

    def output(self):
        return luigi.LocalTarget(path=get_target_path(self))

    def run(self):
        self.output().open("w").close()
        TaskETL().export_data()


def main():
    try:
        luigi.run(main_task_cls=EcmTask())
    except ParamsException as e:
        print(e)
    except Exception as e:
        print(e)


def export_tasks():
    try:
        # Importante ser a ultima tarefa a ser executada pois ela vai executar todas as dependencias
        load_luigi_scheduler()
        luigi.run(main_task_cls=TaskExport())
    except ParamsException as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
