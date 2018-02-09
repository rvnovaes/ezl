# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint, \
    text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class AccountEmailaddres(Base):
    __tablename__ = 'account_emailaddress'

    id = Column(Integer, primary_key=True, server_default=text("nextval('account_emailaddress_id_seq'::regclass)"))
    email = Column(String(254), nullable=False, unique=True)
    verified = Column(Boolean, nullable=False)
    primary = Column(Boolean, nullable=False)
    user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    user = relationship('AuthUser')


class AccountEmailconfirmation(Base):
    __tablename__ = 'account_emailconfirmation'

    id = Column(Integer, primary_key=True, server_default=text("nextval('account_emailconfirmation_id_seq'::regclass)"))
    created = Column(DateTime(True), nullable=False)
    sent = Column(DateTime(True))
    key = Column(String(64), nullable=False, unique=True)
    email_address_id = Column(ForeignKey('account_emailaddress.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    email_address = relationship('AccountEmailaddres')


class Addres(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, server_default=text("nextval('address_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    street = Column(String(255), nullable=False)
    number = Column(String(255), nullable=False)
    complement = Column(String(255), nullable=False)
    city_region = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)
    notes = Column(Text, nullable=False)
    home_address = Column(Boolean, nullable=False)
    business_address = Column(Boolean, nullable=False)
    address_type_id = Column(ForeignKey('address_type.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    city_id = Column(ForeignKey('city.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    country_id = Column(ForeignKey('country.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    state_id = Column(ForeignKey('state.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    address_type = relationship('AddressType')
    alter_user = relationship('AuthUser', primaryjoin='Addres.alter_user_id == AuthUser.id')
    city = relationship('City')
    country = relationship('Country')
    create_user = relationship('AuthUser', primaryjoin='Addres.create_user_id == AuthUser.id')
    state = relationship('State')


class AddressType(Base):
    __tablename__ = 'address_type'

    id = Column(Integer, primary_key=True, server_default=text("nextval('address_type_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='AddressType.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='AddressType.create_user_id == AuthUser.id')


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth_group_id_seq'::regclass)"))
    name = Column(String(80), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        UniqueConstraint('group_id', 'permission_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth_group_permissions_id_seq'::regclass)"))
    group_id = Column(ForeignKey('auth_group.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    permission_id = Column(ForeignKey('auth_permission.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    group = relationship('AuthGroup')
    permission = relationship('AuthPermission')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        UniqueConstraint('content_type_id', 'codename'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth_permission_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    codename = Column(String(100), nullable=False)

    content_type = relationship('DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime(True))
    is_superuser = Column(Boolean, nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    date_joined = Column(DateTime(True), nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth_user_groups_id_seq'::regclass)"))
    user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    group_id = Column(ForeignKey('auth_group.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    group = relationship('AuthGroup')
    user = relationship('AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth_user_user_permissions_id_seq'::regclass)"))
    user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    permission_id = Column(ForeignKey('auth_permission.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    permission = relationship('AuthPermission')
    user = relationship('AuthUser')


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True, server_default=text("nextval('city_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    court_district_id = Column(ForeignKey('court_district.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    state_id = Column(ForeignKey('state.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='City.alter_user_id == AuthUser.id')
    court_district = relationship('CourtDistrict')
    create_user = relationship('AuthUser', primaryjoin='City.create_user_id == AuthUser.id')
    state = relationship('State')


class ContactMechanism(Base):
    __tablename__ = 'contact_mechanism'

    id = Column(Integer, primary_key=True, server_default=text("nextval('contact_mechanism_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    description = Column(String(255), nullable=False, unique=True)
    notes = Column(String(400), nullable=False)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    contact_mechanism_type_id = Column(ForeignKey('contact_mechanism_type.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='ContactMechanism.alter_user_id == AuthUser.id')
    contact_mechanism_type = relationship('ContactMechanismType')
    create_user = relationship('AuthUser', primaryjoin='ContactMechanism.create_user_id == AuthUser.id')


class ContactMechanismType(Base):
    __tablename__ = 'contact_mechanism_type'

    id = Column(Integer, primary_key=True, server_default=text("nextval('contact_mechanism_type_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='ContactMechanismType.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='ContactMechanismType.create_user_id == AuthUser.id')


class ContactU(Base):
    __tablename__ = 'contact_us'

    id = Column(Integer, primary_key=True, server_default=text("nextval('contact_us_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='ContactU.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='ContactU.create_user_id == AuthUser.id')


class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True, server_default=text("nextval('country_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Country.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Country.create_user_id == AuthUser.id')


class CourtDistrict(Base):
    __tablename__ = 'court_district'
    __table_args__ = (
        UniqueConstraint('state_id', 'name'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('court_district_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    state_id = Column(ForeignKey('state.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='CourtDistrict.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='CourtDistrict.create_user_id == AuthUser.id')
    state = relationship('State')


class CourtDivision(Base):
    __tablename__ = 'court_division'

    id = Column(Integer, primary_key=True, server_default=text("nextval('court_division_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    is_active = Column(Boolean, nullable=False)
    legacy_code = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='CourtDivision.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='CourtDivision.create_user_id == AuthUser.id')


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True, server_default=text("nextval('django_admin_log_id_seq'::regclass)"))
    action_time = Column(DateTime(True), nullable=False)
    object_id = Column(Text)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(Text, nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id', deferrable=True, initially='DEFERRED'), index=True)
    user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    content_type = relationship('DjangoContentType')
    user = relationship('AuthUser')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        UniqueConstraint('app_label', 'model'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('django_content_type_id_seq'::regclass)"))
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoMigration(Base):
    __tablename__ = 'django_migrations'

    id = Column(Integer, primary_key=True, server_default=text("nextval('django_migrations_id_seq'::regclass)"))
    app = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    applied = Column(DateTime(True), nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True, index=True)
    session_data = Column(Text, nullable=False)
    expire_date = Column(DateTime(True), nullable=False, index=True)


class DjangoSite(Base):
    __tablename__ = 'django_site'

    id = Column(Integer, primary_key=True, server_default=text("nextval('django_site_id_seq'::regclass)"))
    domain = Column(String(100), nullable=False, unique=True)
    name = Column(String(50), nullable=False)


class Folder(Base):
    __tablename__ = 'folder'

    id = Column(Integer, primary_key=True, server_default=text("nextval('folder_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    legacy_code = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_customer_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Folder.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Folder.create_user_id == AuthUser.id')


class Instance(Base):
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True, server_default=text("nextval('instance_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Instance.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Instance.create_user_id == AuthUser.id')


class LawSuit(Base):
    __tablename__ = 'law_suit'

    id = Column(Integer, primary_key=True, server_default=text("nextval('law_suit_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    folder_id = Column(ForeignKey('folder.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_lawyer_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='LawSuit.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='LawSuit.create_user_id == AuthUser.id')
    folder = relationship('Folder')


class LawsuitLawsuitinstance(Base):
    __tablename__ = 'lawsuit_lawsuitinstance'

    id = Column(Integer, primary_key=True, server_default=text("nextval('lawsuit_lawsuitinstance_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    law_suit_number = Column(String(255), nullable=False, unique=True)
    legacy_code = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    court_district_id = Column(ForeignKey('court_district.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    instance_id = Column(ForeignKey('instance.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    law_suit_id = Column(ForeignKey('law_suit.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_court_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='LawsuitLawsuitinstance.alter_user_id == AuthUser.id')
    court_district = relationship('CourtDistrict')
    create_user = relationship('AuthUser', primaryjoin='LawsuitLawsuitinstance.create_user_id == AuthUser.id')
    instance = relationship('Instance')
    law_suit = relationship('LawSuit')


class Movement(Base):
    __tablename__ = 'movement'

    id = Column(Integer, primary_key=True, server_default=text("nextval('movement_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    legacy_code = Column(String(255), nullable=False, unique=True)
    deadline = Column(DateTime(True))
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_lawyer_id = Column(Integer, nullable=False, index=True)
    type_movement_id = Column(ForeignKey('type_movement.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    law_suit_instance_id = Column(ForeignKey('lawsuit_lawsuitinstance.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Movement.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Movement.create_user_id == AuthUser.id')
    law_suit_instance = relationship('LawsuitLawsuitinstance')
    type_movement = relationship('TypeMovement')


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    legal_name = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    is_lawyer = Column(Boolean, nullable=False)
    legal_type = Column(String(1), nullable=False)
    cpf_cnpj = Column(String(255), nullable=False)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    auth_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), unique=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    is_customer = Column(Boolean, nullable=False)
    is_supplier = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Person.alter_user_id == AuthUser.id')
    auth_user = relationship('AuthUser', uselist=False, primaryjoin='Person.auth_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Person.create_user_id == AuthUser.id')


class State(Base):
    __tablename__ = 'state'

    id = Column(Integer, primary_key=True, server_default=text("nextval('state_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    initials = Column(String(10), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    country_id = Column(ForeignKey('country.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='State.alter_user_id == AuthUser.id')
    country = relationship('Country')
    create_user = relationship('AuthUser', primaryjoin='State.create_user_id == AuthUser.id')


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    legacy_code = Column(String(255), nullable=False, unique=True)
    delegation_date = Column(DateTime(True), nullable=False)
    acceptance_date = Column(DateTime(True))
    final_deadline_date = Column(DateTime(True))
    execution_date = Column(DateTime(True))
    return_date = Column(DateTime(True))
    refused_date = Column(DateTime(True))
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    person_asked_by_id = Column(Integer, nullable=False, index=True)
    person_executed_by_id = Column(Integer, nullable=False, index=True)
    movement_id = Column(ForeignKey('movement.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_movement_id = Column(ForeignKey('type_movement.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    description = Column(Text)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='Task.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='Task.create_user_id == AuthUser.id')
    movement = relationship('Movement')
    type_movement = relationship('TypeMovement')


class TaskEcm(Base):
    __tablename__ = 'task_ecm'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_ecm_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    is_active = Column(Boolean, nullable=False)
    path = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    task_id = Column(ForeignKey('task.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    alter_user = relationship('AuthUser', primaryjoin='TaskEcm.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='TaskEcm.create_user_id == AuthUser.id')
    task = relationship('Task')


class TaskTaskhistory(Base):
    __tablename__ = 'task_taskhistory'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_taskhistory_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    notes = Column(Text)
    status = Column(String(10), nullable=False)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    task_id = Column(ForeignKey('task.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    create_user = relationship('AuthUser')
    task = relationship('Task')


class TypeMovement(Base):
    __tablename__ = 'type_movement'

    id = Column(Integer, primary_key=True, server_default=text("nextval('type_movement_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    name = Column(String(255), nullable=False, unique=True)
    legacy_code = Column(String(255), nullable=False, unique=True)
    uses_wo = Column(Boolean, nullable=False)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='TypeMovement.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='TypeMovement.create_user_id == AuthUser.id')


class TypeTask(Base):
    __tablename__ = 'type_task'

    id = Column(Integer, primary_key=True, server_default=text("nextval('type_task_id_seq'::regclass)"))
    create_date = Column(DateTime(True), nullable=False)
    alter_date = Column(DateTime(True))
    is_active = Column(Boolean, nullable=False)
    legacy_code = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    alter_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), index=True)
    create_user_id = Column(ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    system_prefix = Column(String(255), nullable=False)

    alter_user = relationship('AuthUser', primaryjoin='TypeTask.alter_user_id == AuthUser.id')
    create_user = relationship('AuthUser', primaryjoin='TypeTask.create_user_id == AuthUser.id')
