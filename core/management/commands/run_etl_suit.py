from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def handle(self, *args, **options):
        self.run_user_etl()
