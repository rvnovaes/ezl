from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def add_arguments(self, parser):
        parser.add_argument('etls', choices=['user'])

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_ecm_etl(self):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl().import_data()

    def run_etl(self):
        from etl.advwin_ezl.luigi_jobs import main
        main()

    def handle(self, *args, **options):
        if 'user' in options['etls']:
            self.run_user_etl()
