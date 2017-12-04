from django.core.management.base import BaseCommand

import luigi


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def add_arguments(self, parser):
        parser.add_argument('etl', choices=['user', 'ecm', 'luigi', 'folder',
        'lawsuit', 'movement', 'task'])

        parser.add_argument(
            '--task_legacy_code',
            dest='task_legacy_code',
            default=False,
            help='Importa ECM de uma task especifica'
        )

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_folder_etl(self):
        from etl.advwin_ezl.law_suit.folder import FolderETL
        FolderETL().import_data()

    def run_lawsuit_etl(self):
        from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
        LawsuitETL().import_data()

    def run_movement_etl(self):
        from etl.advwin_ezl.law_suit.movement import MovementETL
        MovementETL().import_data()

    def run_task_etl(self):
        from etl.advwin_ezl.task.task    import TaskETL
        TaskETL().import_data()

    def run_ecm_etl(self):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl(task_legacy_code=task_legacy_code).import_data()

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
        options = {
        'user': self.run_user_etl,
        'folder': self.run_folder_etl,
        'lawsuit': self.run_lawsuit_etl,
        'movement': self.run_movement_etl,
        'task': self.run_task_etl,
        'ecm': self.run_ecm_etl,
        'luigi': self.run_luigi
        }
        options.get(etl)()
