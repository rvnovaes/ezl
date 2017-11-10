from django.core.management.base import BaseCommand

import luigi


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def add_arguments(self, parser):
        parser.add_argument('etl', choices=['user', 'ecm', 'lawsuit', 'movement', 'task', 'luigi'])

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_ecm_etl(self):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl().import_data()

    def run_lawsuit_etl(self):
        from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
        LawsuitETL().import_data()

    def run_movement_etl(self):
        from etl.advwin_ezl.law_suit.movement import MovementETL
        MovementETL().import_data()

    def run_task_etl(self):
        from etl.advwin_ezl.task.task import TaskETL
        TaskETL().import_data()

    def run_luigi(self):
        from etl.advwin_ezl.luigi_jobs import EcmTask
        luigi.build([EcmTask()])

    def handle(self, *args, **options):
        etl = options['etl']
        if etl == 'user':
            self.run_user_etl()

        elif etl == 'ecm':
            self.run_ecm_etl()

        elif etl == 'lawsuit':
            self.run_lawsuit_etl()

        elif etl == 'movement':
            self.run_movement_etl()

        elif etl == 'task':
            self.run_task_etl()

        elif etl == 'luigi':
            self.run_luigi()
