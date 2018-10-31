from django.core.management.base import BaseCommand
from core.models import Office
from core.permissions import *


class Command(BaseCommand):
    help = ('Create groups and associate the task model permissions with them.')

    def handle(self, *args, **options):
        for office in Office.objects.all():
            create_permission(office)