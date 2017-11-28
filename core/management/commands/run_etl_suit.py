from django.core.management.base import BaseCommand

import luigi


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def add_arguments(self, parser):
        parser.add_argument(
            'etl', choices=['user', 'ecm', 'luigi'])

        parser.add_argument(
            '--task_legacy_code',
            dest='task_legacy_code',
            default=False,
            help='Importa ECM de uma task especifica'
        )

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_ecm_etl(self, task_legacy_code=False):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl(task_legacy_code=task_legacy_code).import_data()

    def run_luigi(self):
        from etl.advwin_ezl.luigi_jobs import EcmTask
        luigi.build([EcmTask()])

    def handle(self, *args, **options):        
        etl = options['etl']
        if etl == 'user':
            self.run_user_etl()

        elif etl == 'ecm':
            self.run_ecm_etl(task_legacy_code=options['task_legacy_code'])

        elif etl == 'luigi':
            self.run_luigi()
