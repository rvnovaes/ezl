import os
import sys

import django
from django.db import connection

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Country, State, City, Person
from lawsuit.models import TypeMovement, Instance, Folder, CourtDivision, CourtDistrict, LawSuit, Movement
from task.models import TypeTask, Task, TaskStatus, TaskHistory

invalid_registry = '-INVÁLIDO'


class InvalidObjectFactory(object):
    models = [Person, TypeMovement, Instance, Folder, CourtDivision, LawSuit, Movement, TypeTask,
              Task, CourtDistrict, Country, State, City, User, TaskHistory]

    @staticmethod
    def create():
        # cria usuário padrão

        user = User.objects.create_superuser('invalid_user', 'invalid_user@mttech.com.br', 'abc123456*')
        admin = User.objects.create_superuser('admin', 'admin@mttech.com.br', 'abc123456*')

        # Registros inválidos para o app core
        invalid_country, created = Country.objects.get_or_create(
            name=Country._meta.verbose_name.upper() + invalid_registry,
            create_user=user)
        invalid_state, created = State.objects.get_or_create(
            name=State._meta.verbose_name.upper() + invalid_registry,
            create_user=user, country=invalid_country)
        invalid_court_district, created = CourtDistrict.objects.get_or_create(create_user=user,
                                                                              name=CourtDistrict._meta.verbose_name.upper()
                                                                                   + invalid_registry,
                                                                              state=invalid_state)
        invalid_city, created = City.objects.get_or_create(
            name=City._meta.verbose_name.upper() + invalid_registry,
            state=invalid_state, create_user=user,
            court_district=invalid_court_district)

        invalid_person, created = Person.objects.get_or_create(
            legal_name=Person._meta.verbose_name.upper() + invalid_registry
            , create_user=user)
        # Registros inválidos para o app lawsuit
        invalid_type_movement, created = TypeMovement.objects.get_or_create(
            name=TypeMovement._meta.verbose_name.upper() +
                 invalid_registry, create_user=user)
        invalid_instance, created = Instance.objects.get_or_create(name=Instance._meta.verbose_name.upper() +
                                                                        invalid_registry, create_user=user)
        invalid_folder, created = Folder.objects.get_or_create(person_customer=invalid_person, create_user=user)

        invalid_court_division, created = CourtDivision.objects.get_or_create(
            name=CourtDivision._meta.verbose_name.upper()
                 + invalid_registry, create_user=user)

        invalid_law_suit, created = LawSuit.objects.get_or_create(create_user=user, person_court=invalid_person,
                                                                  folder=invalid_folder,
                                                                  person_lawyer=invalid_person,
                                                                  court_district=invalid_court_district,
                                                                  instance=invalid_instance,
                                                                  court_division=invalid_court_division,
                                                                  law_suit_number=LawSuit._meta.verbose_name.upper() + invalid_registry)
        invalid_movement, created = Movement.objects.get_or_create(create_user=user, law_suit=invalid_law_suit,
                                                                   person_lawyer=invalid_person,
                                                                   type_movement=invalid_type_movement)

        # Registros inválidos para o app Task
        invalid_type_task, created = TypeTask.objects.get_or_create(create_user=user,
                                                                    name=TypeTask._meta.verbose_name.upper() + invalid_registry)
        invalid_task, created = Task.objects.get_or_create(create_user=user, movement=invalid_movement,
                                                           person_asked_by=invalid_person,
                                                           person_executed_by=invalid_person,
                                                           task_status=TaskStatus.INVALID, type_task=invalid_type_task)

    @staticmethod
    def get_invalid_model(model):
        return model.objects.get(id=1)

    def restart_table_id(self):
        with connection.cursor() as cursor:
            for model in self.models:
                cursor.execute("TRUNCATE TABLE " + model._meta.db_table + " RESTART IDENTITY CASCADE;")


if __name__ == '__main__':
    InvalidObjectFactory().restart_table_id()
    InvalidObjectFactory.create()
