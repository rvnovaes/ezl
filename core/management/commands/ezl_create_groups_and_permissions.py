from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from core.models import Person, Office
from task.models import Permissions
from survey.models import SurveyPermissions
from core.permissions import *


class Command(BaseCommand):
    help = ('Create groups and associate the task model permissions with them.')

    def handle(self, *args, **options):
        for office in Office.objects.all():
            create_permission(office)