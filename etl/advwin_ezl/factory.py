import os
import sys

import django
from django.db import connection

from etl.advwin_ezl import settings

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Country, State, City, Person, Address, AddressType, ContactMechanism, ContactMechanismType
from lawsuit.models import TypeMovement, Instance, Folder, CourtDivision, CourtDistrict, LawSuit, Movement
from task.models import TypeTask, Task, TaskStatus, TaskHistory
from core import signals

invalid_registry = '-INVÁLIDO'
invalid_legacy_code = 'REGISTRO' + invalid_registry


class InvalidObjectFactory(object):
    models = [Person, TypeMovement, Instance, Folder, CourtDivision, LawSuit, Movement, TypeTask,
              Task, CourtDistrict, Country, State, City, User, TaskHistory]

    @staticmethod
    def create():
        # cria usuário padrão
        signals
        user = User.objects.filter(username='invalid_user').first()
        admin = User.objects.filter(username='admin').first()
        if not user:
            user = User.objects.create_superuser('invalid_user', 'invalid_user@mttech.com.br', 'admin')
        if not admin:
            admin = User.objects.create_superuser('admin', 'admin@mttech.com.br', 'admin')

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

        #Atualiza os dados de invalid_person para o padrao
        invalid_user = User.objects.filter(username='invalid_user').first().id
        invalid_person = Person.objects.filter(auth_user_id=invalid_user).first()
        Person.objects.filter(auth_user_id=invalid_user).update(legacy_code=invalid_legacy_code,
                                legal_name=Person._meta.verbose_name.upper() + invalid_registry,
                                name=Person._meta.verbose_name.upper() + invalid_registry)
        # Registros inválidos para o app lawsuit
        invalid_type_movement, created = TypeMovement.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=TypeMovement._meta.verbose_name.upper() +
                 invalid_registry, create_user=user)

        invalid_instance, created = Instance.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=Instance._meta.verbose_name.upper() +
                 invalid_registry, create_user=user)
        invalid_folder, created = Folder.objects.get_or_create(legacy_code=invalid_legacy_code,
                                                               person_customer=invalid_person, create_user=user)

        invalid_court_division, created = CourtDivision.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=CourtDivision._meta.verbose_name.upper()
                 + invalid_registry, create_user=user)

        invalid_law_suit, created = LawSuit.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            create_user=user, person_court=invalid_person,
            folder=invalid_folder,
            person_lawyer=invalid_person,
            court_district=invalid_court_district,
            instance=invalid_instance,
            court_division=invalid_court_division,
            law_suit_number=LawSuit._meta.verbose_name.upper() + invalid_registry)

        invalid_movement, created = Movement.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            create_user=user, law_suit=invalid_law_suit,
            type_movement=invalid_type_movement)

        invalid_address_type, created = AddressType.objects.get_or_create(
            name=AddressType._meta.verbose_name.upper() + invalid_registry, create_user=user
        )

        invalid_address, created = Address.objects.get_or_create(
            address_type=invalid_address_type,
            street=Address._meta.verbose_name.upper() + invalid_registry,
            number=Address._meta.verbose_name.upper() + invalid_registry,
            complement=Address._meta.verbose_name.upper() + invalid_registry,
            city_region=Address._meta.verbose_name.upper() + invalid_registry,
            zip_code=Address._meta.verbose_name.upper() + invalid_registry,
            notes=Address._meta.verbose_name.upper() + invalid_registry,
            city=invalid_city,
            state=invalid_state,
            country=invalid_country,
            person=invalid_person,
            create_user=user
        )

        invalid_contact_mechanism_type, created = ContactMechanismType.objects.get_or_create(
            name=ContactMechanismType._meta.verbose_name.upper() + invalid_registry, create_user=user
        )

        invalid_contact_mechanism, created = ContactMechanism.objects.get_or_create(
            contact_mechanism_type=invalid_contact_mechanism_type,
            description=ContactMechanism._meta.verbose_name.upper() + invalid_registry,
            notes=ContactMechanism._meta.verbose_name.upper() + invalid_registry,
            person=invalid_person, create_user=user
        )

        # Registros inválidos para o app Task
        invalid_type_task, created = TypeTask.objects.get_or_create(create_user=user, legacy_code=invalid_legacy_code,
                                                                    name=TypeTask._meta.verbose_name.upper() + invalid_registry)
        invalid_task, created = Task.objects.get_or_create(create_user=user, movement=invalid_movement,
                                                           person_asked_by=invalid_person,
                                                           person_executed_by=invalid_person,
                                                           legacy_code=invalid_legacy_code,
                                                           task_status=TaskStatus.INVALID, type_task=invalid_type_task)

    @staticmethod
    def get_invalid_model(model):
        return model.objects.get(id=1)

    def restart_table_id(self):
        if settings.TRUNCATE_ALL_TABLES:
            with connection.cursor() as cursor:
                for model in self.models:
                    cursor.execute("TRUNCATE TABLE " + model._meta.db_table + " RESTART IDENTITY CASCADE;")


if __name__ == '__main__':
    InvalidObjectFactory().restart_table_id()
    InvalidObjectFactory.create()
