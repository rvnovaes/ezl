from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_ecm_etl(self):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl().import_data()

    def handle(self, *args, **options):
        self.run_ecm_etl()


