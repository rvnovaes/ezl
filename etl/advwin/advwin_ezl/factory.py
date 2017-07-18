import os
import sys

import django

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Country, State, City, Person
from lawsuit.models import TypeMovement, Instance, Folder, CourtDivision, CourtDistrict, LawSuit, Movement
from task.models import TypeTask, Task, TaskStatus

invalid_registry = '-INVÁLIDO'


class InvalidObjectFactory(object):
    @staticmethod
    def create():
        # cria usuário padrão
        user = User.objects.create_superuser('admin', 'admin@mttech.com.br', 'abc123456*', id=1)

        # Registros inválidos para o app core
        invalid_country, created = Country.objects.get_or_create(id=1,
                                                                 name=Country._meta.verbose_name.upper() + invalid_registry,
                                                                 create_user=user)
        invalid_state, created = State.objects.get_or_create(id=1,
                                                             name=State._meta.verbose_name.upper() + invalid_registry,
                                                             create_user=user, country=invalid_country)
        invalid_court_district, created = CourtDistrict.objects.get_or_create(id=1, create_user=user,
                                                                              name=CourtDistrict._meta.verbose_name.upper()
                                                                                   + invalid_registry,
                                                                              state=invalid_state)
        invalid_city, created = City.objects.get_or_create(id=1,
                                                           name=City._meta.verbose_name.upper() + invalid_registry,
                                                           state=invalid_state, create_user=user,
                                                           court_district=invalid_court_district)

        invalid_person, created = Person.objects.get_or_create(id=1,
                                                               legal_name=Person._meta.verbose_name.upper() + invalid_registry
                                                               , create_user=user)
        # Registros inválidos para o app lawsuit
        invalid_type_movement, created = TypeMovement.objects.get_or_create(id=1,
                                                                            name=TypeMovement._meta.verbose_name.upper() +
                                                                                 invalid_registry, create_user=user)
        invalid_instance, created = Instance.objects.get_or_create(id=1, name=Instance._meta.verbose_name.upper() +
                                                                              invalid_registry, create_user=user)
        invalid_folder, created = Folder.objects.get_or_create(id=1, person_customer=invalid_person, create_user=user)

        invalid_court_division, created = CourtDivision.objects.get_or_create(id=1,
                                                                              name=CourtDivision._meta.verbose_name.upper()
                                                                                   + invalid_registry, create_user=user)

        invalid_law_suit, created = LawSuit.objects.get_or_create(id=1, create_user=user, person_court=invalid_person,
                                                                  folder=invalid_folder,
                                                                  person_lawyer=invalid_person,
                                                                  court_district=invalid_court_district,
                                                                  instance=invalid_instance,
                                                                  court_division=invalid_court_division,
                                                                  law_suit_number=LawSuit._meta.verbose_name + invalid_registry)
        invalid_movement, created = Movement.objects.get_or_create(id=1, create_user=user, law_suit=invalid_law_suit,
                                                                   person_lawyer=invalid_person,
                                                                   type_movement=invalid_type_movement)

        # Registros inválidos para o app Task
        invalid_type_task, created = TypeTask.objects.get_or_create(id=1, create_user=user,
                                                                    name=TypeTask._meta.verbose_name.upper() + invalid_registry)
        invalid_task, created = Task.objects.get_or_create(id=1, create_user=user, movement=invalid_movement,
                                                           person_asked_by=invalid_person,
                                                           person_executed_by=invalid_person,
                                                           task_status=TaskStatus.INVALID, type_task=invalid_type_task)

    @staticmethod
    def get_invalid_model(model):
        return model.Objects.get(id=1)


if __name__ == '__main__':
    InvalidObjectFactory.create()
