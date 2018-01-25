from config.config import get_parser
from django.db import connection
from django.contrib.auth.models import User

from core.models import Country, State, City, Person, Address, AddressType, ContactMechanism, \
    ContactMechanismType, Office
from core import signals
from lawsuit.models import TypeMovement, Instance, Folder, CourtDivision, CourtDistrict, LawSuit, \
    Movement, Organ
from task.models import TypeTask, Task, TaskStatus, TaskHistory
from financial.models import CostCenter
from etl.utils import get_default_office


config_parser = get_parser()
settings = config_parser['etl']

invalid_registry = '-INVÁLIDO'
invalid_legacy_code = 'REGISTRO' + invalid_registry
INVALID_ORGAN = Organ._meta.verbose_name.upper() + invalid_registry


class InvalidObjectFactory(object):
    models = [Person, TypeMovement, Instance, Folder, CourtDivision, LawSuit, Movement, TypeTask,
              Task, CourtDistrict, Country, State, City, User, TaskHistory, CostCenter]

    @staticmethod
    def create():
        # cria usuário padrão

        print(signals)
        user = User.objects.filter(username='invalid_user').first()
        admin = User.objects.filter(username='admin').first()
        if not user:
            user = User.objects.create_superuser('invalid_user', 'invalid_user@mttech.com.br',
                                                 'admin')
        if not admin:
            admin = User.objects.create_superuser('admin', 'admin@mttech.com.br', 'admin')

        default_office = get_default_office()

        # Registros inválidos para o app core
        invalid_country, created = Country.objects.get_or_create(
            name=Country._meta.verbose_name.upper() + invalid_registry,
            create_user=user)
        invalid_state, created = State.objects.get_or_create(
            name=State._meta.verbose_name.upper() + invalid_registry,
            create_user=user, country=invalid_country)
        invalid_court_district, created = CourtDistrict.objects.get_or_create(
            create_user=user,
            name=CourtDistrict._meta.verbose_name.upper() + invalid_registry,
            state=invalid_state)
        invalid_city, created = City.objects.get_or_create(
            name=City._meta.verbose_name.upper() + invalid_registry,
            state=invalid_state, create_user=user,
            court_district=invalid_court_district)

        # Atualiza os dados de invalid_person para o padrao
        invalid_user = User.objects.filter(username='invalid_user').first().id
        invalid_person = Person.objects.filter(auth_user_id=invalid_user).first()
        Person.objects.filter(auth_user_id=invalid_user).update(
                              legacy_code=invalid_legacy_code,
                              legal_name=Person._meta.verbose_name.upper() + invalid_registry,
                              name=Person._meta.verbose_name.upper() + invalid_registry)

        # Registros inválidos para o app lawsuit
        invalid_organ, created = Organ.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            legal_name=INVALID_ORGAN,
            court_district=invalid_court_district,
            create_user=user,
            office=default_office
        )
        invalid_type_movement, created = TypeMovement.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=TypeMovement._meta.verbose_name.upper() + invalid_registry, create_user=user,
            office=default_office)

        invalid_instance, created = Instance.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=Instance._meta.verbose_name.upper() + invalid_registry, create_user=user,
            office=default_office)
        invalid_folder, created = Folder.objects.get_or_create(legacy_code=invalid_legacy_code,
                                                               person_customer=invalid_person,
                                                               create_user=user,
                                                               office=default_office)

        invalid_court_division, created = CourtDivision.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            name=CourtDivision._meta.verbose_name.upper() + invalid_registry, create_user=user,
            office=default_office)

        invalid_law_suit, created = LawSuit.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            create_user=user, organ=invalid_organ,
            folder=invalid_folder,
            person_lawyer=invalid_person,
            court_district=invalid_court_district,
            instance=invalid_instance,
            court_division=invalid_court_division,
            law_suit_number=LawSuit._meta.verbose_name.upper() + invalid_registry,
            office=default_office)

        invalid_movement, created = Movement.objects.get_or_create(
            legacy_code=invalid_legacy_code,
            create_user=user, law_suit=invalid_law_suit,
            folder=invalid_folder,
            type_movement=invalid_type_movement,
            office=default_office)

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
            name=ContactMechanismType._meta.verbose_name.upper() + invalid_registry,
            create_user=user
        )

        invalid_contact_mechanism, created = ContactMechanism.objects.get_or_create(
            contact_mechanism_type=invalid_contact_mechanism_type,
            description=ContactMechanism._meta.verbose_name.upper() + invalid_registry,
            notes=ContactMechanism._meta.verbose_name.upper() + invalid_registry,
            person=invalid_person, create_user=user
        )

        # Registros inválidos para o app Task
        invalid_type_task, created = TypeTask.objects.get_or_create(
            create_user=user,
            legacy_code=invalid_legacy_code,
            name=TypeTask._meta.verbose_name.upper() + invalid_registry,
            office=default_office)

        invalid_task, created = Task.objects.get_or_create(create_user=user,
                                                           movement=invalid_movement,
                                                           person_asked_by=invalid_person,
                                                           person_executed_by=invalid_person,
                                                           legacy_code=invalid_legacy_code,
                                                           task_status=TaskStatus.INVALID,
                                                           type_task=invalid_type_task,
                                                           office=default_office)

        # Registro inválido de centro de custo
        CostCenter.objects.get_or_create(
            create_user=user,
            name=CostCenter._meta.verbose_name.upper() + invalid_registry,
            legacy_code=invalid_legacy_code,
            office=default_office
        )

    @staticmethod
    def get_invalid_model(model):
        return model.objects.get(id=1)

    def restart_table_id(self):
        if settings['truncate_all_tables']:
            with connection.cursor() as cursor:
                for model in self.models:
                    cursor.execute('TRUNCATE TABLE ' +
                                   model._meta.db_table +
                                   ' RESTART IDENTITY CASCADE;')


class DefaultOffice(object):

    @staticmethod
    def create():
        admin = User.objects.filter(username='admin').first()
        admin_person = Person.objects.filter(auth_user=admin).first()
        default_office = get_default_office()
        default_office.persons.add(admin_person)


if __name__ == '__main__':
    InvalidObjectFactory().restart_table_id()
    InvalidObjectFactory.create()
    DefaultOffice.create()
