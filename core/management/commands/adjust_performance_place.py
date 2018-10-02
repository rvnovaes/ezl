from django.core.management.base import BaseCommand
from task.models import Task


class Command(BaseCommand):
    help = ('replace default performance place with the court_district in task lawsuit.')

    def handle(self, *args, **options):
        court_districts = list(set(Task.objects.all().values_list('movement__law_suit__court_district','movement__law_suit__court_district__name','movement__law_suit__court_district__state__initials')))
        for court_district in court_districts:
            print('Atualizando registros com comarca {} ({})'.format(court_district[1], court_district[2]))
            Task.objects.filter(movement__law_suit__court_district=court_district[0]).update(
                performance_place='{} ({})'.format(court_district[1], court_district[2]))
