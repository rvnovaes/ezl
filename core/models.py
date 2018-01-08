from enum import Enum

from django.conf import settings
from django.db import models

from core.managers import PersonManager
from core.utils import LegacySystem


class LegalType(Enum):
    FISICA = 'F'
    JURIDICA = 'J'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

    @staticmethod
    def format(value):
        """
        Mostra os tipos de pessoa de forma correta, com acento

        :param value: Valor selecionado sendo F ou J
        :type value: str
        :return: Retorna o valor a ser mostrado na tela para o usuario final
        :rtype: str
        """
        label = {'F': 'Física', 'J': 'Jurídica'}
        return label.get(value)


class AuditCreate(models.Model):
    # auto_now_add - toda vez que for criado
    create_date = models.DateTimeField('Criado em', auto_now_add=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='%(class)s_create_user',
                                    verbose_name='Criado por')

    class Meta:
        abstract = True


class AuditAlter(models.Model):
    # auto_now - toda vez que for salvo
    alter_date = models.DateTimeField('Atualizado em', auto_now=True, blank=True, null=True)
    alter_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True,
                                   null=True,
                                   related_name='%(class)s_alter_user',
                                   verbose_name='Alterado por')

    class Meta:
        abstract = True


class LegacyCode(models.Model):
    legacy_code = models.CharField(max_length=255, blank=True, null=True,
                                   verbose_name='Código legado')
    system_prefix = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name='Prefixo do sistema',
                                     choices=((x.value, x.name.title()) for x in LegacySystem))

    class Meta:
        abstract = True
        unique_together = (('legacy_code', 'system_prefix'),)


class Audit(AuditCreate, AuditAlter):
    is_active = models.BooleanField(null=False, default=True, verbose_name='Ativo')

    class Meta:
        abstract = True

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class AddressType(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        db_table = 'address_type'

    def __str__(self):
        return self.name


class Country(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        db_table = 'country'
        verbose_name = 'País'

    def __str__(self):
        return self.name


class State(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)
    initials = models.CharField(max_length=10, null=False, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = 'state'
        verbose_name = 'Estado'

    def __str__(self):
        return self.name


class City(Audit):
    name = models.CharField(max_length=255, null=False)
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=False, null=False)

    court_district = models.ForeignKey('lawsuit.CourtDistrict', on_delete=models.PROTECT,
                                       blank=False, null=False,
                                       verbose_name='Comarca')

    class Meta:
        db_table = 'city'
        verbose_name = 'Cidade'
        unique_together = (('name', 'state'),)

    def __str__(self):
        return self.name


class AbstractPerson(Audit, LegacyCode):
    ADMINISTRATOR_GROUP = 'Administrador'
    CORRESPONDENT_GROUP = 'Correspondente'
    REQUESTER_GROUP = 'Solicitante'
    SERVICE_GROUP = 'Service'
    SUPERVISOR_GROUP = 'Supervisor'
    legal_name = models.CharField(max_length=255, blank=False,
                                  verbose_name='Razão social/Nome completo')
    name = models.CharField(max_length=255, null=True, blank=True,
                            verbose_name='Nome Fantasia/Apelido')
    is_lawyer = models.BooleanField(null=False, default=False, verbose_name='É Advogado?')
    legal_type = models.CharField(null=False, verbose_name='Tipo', max_length=1,
                                  choices=((x.value, x.format(x.value)) for x in LegalType),
                                  default=LegalType.JURIDICA)
    cpf_cnpj = models.CharField(max_length=255, blank=True, null=True,
                                unique=True, verbose_name='CPF/CNPJ')
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     blank=True, null=True,
                                     verbose_name='Usuário do sistema')
    is_customer = models.BooleanField(null=False, default=False, verbose_name='É Cliente?')
    is_supplier = models.BooleanField(null=False, default=False, verbose_name='É Fornecedor?')

    @property
    def cpf(self):
        return self.cpf_cnpj

    @cpf.setter
    def cpf(self, value):
        self.cpf = value

    @property
    def cnpj(self):
        return self.cpf_cnpj

    @cnpj.setter
    def cnpj(self, value):
        self.cnpj = value

    def contact_mechanism_by_type(self, type, formated=True):
        type = ContactMechanismType.objects.filter(name__iexact=type).first()
        contacts = self.contactmechanism_set.filter(contact_mechanism_type=type)
        items = [contact.description for contact in contacts]
        if formated:
            return ' | '.join(items) if items else ''
        return items

    @property
    def emails(self):
        emails = self.get_emails()
        return ' | '.join(emails) if emails else ''

    @property
    def phones(self):
        return self.contact_mechanism_by_type('telefone')

    def get_emails(self):
        emails = set(self.contact_mechanism_by_type('email', formated=False))
        if (self.auth_user and self.auth_user.email and
                self.auth_user.email.strip()):
            emails.add(self.auth_user.email.strip())
        return list(emails)

    def get_phones(self):
        return self.contact_mechanism_by_type('telefone', formated=False)

    def get_address(self):
        return self.address_set.exclude(id=1)

    class Meta:
        abstract = True

    def __str__(self):
        return self.legal_name


class Person(AbstractPerson):
    objects = PersonManager()
    class Meta:
        db_table = 'person'
        ordering = ['legal_name', 'name']
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'


class Office(AbstractPerson):
    persons = models.ManyToManyField(Person, blank=True, related_name='offices')
    offices = models.ManyToManyField('self', blank=True)

    class Meta:
        verbose_name = 'Escritório'


class OfficeMixin(models.Model):
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=False,
                                   null=False,
                                   related_name='%(class)s_office',
                                   verbose_name='Escritório')

    class Meta:
        abstract = True

class Invite(Audit):
    person = models.ForeignKey(Person, blank=False, null=False,
        related_name='invites')
    office = models.ForeignKey(Office, blank=False, null=False)

    class Meta:
        verbose_name = 'Convite'

class Address(Audit):
    address_type = models.ForeignKey(
        AddressType, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Tipo')
    street = models.CharField(max_length=255, verbose_name='Logradouro')
    number = models.CharField(max_length=255, verbose_name='Número')
    complement = models.CharField(max_length=255, blank=True, verbose_name='Complemento')
    city_region = models.CharField(max_length=255, verbose_name='Bairro')
    zip_code = models.CharField(max_length=255, verbose_name='CEP')
    notes = models.TextField(blank=True, verbose_name='Observação')
    home_address = models.BooleanField(default=False, blank=True)
    business_address = models.BooleanField(default=False, blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=False, null=False,
                             verbose_name='Cidade')
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=False, null=False,
                             verbose_name='Estado')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=False, null=False,
                             verbose_name='País')
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'address'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        tpl = '{street}, {number}{complement} - {city_region} - {city} - {state} - CEP {zip_code}'
        return tpl.format(
            number=self.number, street=self.street, city_region=self.city_region,
            city=self.city.name,
            state=self.state.name, zip_code=self.zip_code,
            complement='/' + self.complement if self.complement else ''
        )


class ContactMechanismType(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        db_table = 'contact_mechanism_type'

    def __str__(self):
        return self.name


class ContactMechanism(Audit):
    contact_mechanism_type = models.ForeignKey(
        ContactMechanismType, on_delete=models.PROTECT, blank=False, null=False)
    description = models.CharField(max_length=255, null=False, unique=True)
    notes = models.CharField(max_length=400, blank=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = 'contact_mechanism'

    def __str__(self):
        return self.description


class ContactUs(Audit):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        db_table = 'contact_us'

    def __str__(self):
        return self.name


class ModelExportHistory(models.Model):
    model = models.CharField(max_length=255, unique=True, null=False)
