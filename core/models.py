from enum import Enum

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import LegacySystem


class LegalType(Enum):
    FISICA = u"F"
    JURIDICA = u"J"

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class AuditCreate(models.Model):
    # auto_now_add - toda vez que for criado
    create_date = models.DateTimeField('Criado em', auto_now_add=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='%(class)s_create_user')

    class Meta:
        abstract = True


class AuditAlter(models.Model):
    # auto_now - toda vez que for salvo
    alter_date = models.DateTimeField('Atualizado em', auto_now=True, blank=True, null=True)
    alter_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True,
                                   related_name='%(class)s_alter_user')

    class Meta:
        abstract = True


class LegacyCode(models.Model):
    legacy_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Código legado')
    system_prefix = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'Prefixo do sistema',
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
        db_table = "address_type"

    def __str__(self):
        return self.name


class Country(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name


class State(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)
    initials = models.CharField(max_length=10, null=False, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "state"

    def __str__(self):
        return self.name


class City(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=False, null=False)

    court_district = models.ForeignKey('lawsuit.CourtDistrict', on_delete=models.PROTECT, blank=False, null=False,
                                       verbose_name='Comarca')

    class Meta:
        db_table = "city"

    def __str__(self):
        return self.name


class Person(Audit, LegacyCode):
    legal_name = models.CharField(max_length=255, verbose_name="Razão social/Nome completo")
    name = models.CharField(max_length=255, null=True, blank=True, default=legal_name,
                            verbose_name="Nome Fantasia/Apelido")
    is_lawyer = models.BooleanField(null=False, default=False, verbose_name="É Advogado?")
    is_correspondent = models.BooleanField(null=False, default=False, verbose_name="É Correspondente?")
    is_court = models.BooleanField(null=False, default=False, verbose_name="É Tribunal?")
    legal_type = models.CharField(null=False, verbose_name="Tipo", max_length=1,
                                  choices=((x.value, x.name.title()) for x in LegalType),
                                  default=LegalType.JURIDICA)
    cpf_cnpj = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="CPF/CNPJ")
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True,
                                     verbose_name="Usuário do sistema")
    is_customer = models.BooleanField(null=False, default=False, verbose_name="É Cliente?")
    is_supplier = models.BooleanField(null=False, default=False, verbose_name="É Fornecedor?")

    class Meta:
        db_table = "person"
        ordering = ['-id']
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

    def __str__(self):
        return self.legal_name

    # def post_save_user(sender, instance, created, **kwargs):
    #     if created:
    #         Person.objects.create(
    #             auth_user=instance,
    #             # legal_name=kwargs['legal_name'],
    #             legal_name=instance.username,
    #             name=(instance.first_name + ' ' + instance.last_name) or instance.username,
    #             is_lawyer=False,
    #             is_correspondent=True,
    #             is_court=False,
    #             legal_type='J',
    #             cpf_cnpj=' ',
    #             alter_user=instance,
    #             create_user=instance,
    #             is_customer=False,
    #             is_supplier=True,
    #             is_active=True)
    #     else:
    #         instance.person.save(
    #             update_fields=[
    #                 'alter_date',
    #                 'legal_name',
    #                 'name',
    #                 'is_lawyer',
    #                 'is_correspondent',
    #                 'is_court',
    #                 'legal_type',
    #                 'cpf_cnpj',
    #                 'alter_user',
    #                 'is_active',
    #                 'is_customer',
    #                 'is_supplier'])
    #
    # # dispatch_uid - A unique identifier for a signal receiver in cases where duplicate signals may be sent.
    # models.signals.post_save.connect(post_save_user, sender=User, dispatch_uid='post_save_user')


class Address(Audit):
    address_type = models.ForeignKey(AddressType, on_delete=models.PROTECT, blank=False, null=False)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    complement = models.CharField(max_length=255, blank=True)
    city_region = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    home_address = models.BooleanField(default=False, blank=True)
    business_address = models.BooleanField(default=False, blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=False, null=False)
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=False, null=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=False, null=False)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "address"

    def __str__(self):
        return self.street  # TODO refazer o retorno padrao para descrever o endereço


class ContactMechanismType(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        db_table = "contact_mechanism_type"

    def __str__(self):
        return self.name


class ContactMechanism(Audit):
    contact_mechanism_type = models.ForeignKey(ContactMechanismType, on_delete=models.PROTECT, blank=False, null=False)
    description = models.CharField(max_length=255, null=False, unique=True)
    notes = models.CharField(max_length=400)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "contact_mechanism"

    def __str__(self):
        return self.description


class ContactUs(Audit):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        db_table = "contact_us"

    def __str__(self):
        return self.name
