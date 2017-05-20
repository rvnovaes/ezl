from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# from lawsuit.models import CourtDistrict

LEGAL_TYPE_CHOICES = {
    ('F', 'Física'),
    ('J', 'Jurídica'),
}

class Audit(models.Model):
    create_date = models.DateTimeField()
    alter_date = models.DateTimeField(blank=True, null=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='%(class)s_create_user')
    alter_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True,
                                   related_name='%(class)s_alter_user')
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        abstract = True


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


class Person(Audit):
    legal_name = models.CharField(max_length=255, null=False, unique=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    is_lawyer = models.BooleanField(null=False, default=False)
    is_corresponding = models.BooleanField(null=False, default=False)
    is_court = models.BooleanField(null=False, default=False)
    legal_type = models.CharField(max_length=1, choices=LEGAL_TYPE_CHOICES)
    cpf_cnpj = models.CharField(max_length=255, blank=True)
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = "person"
        ordering = ['-id']

    def __str__(self):
        return self.legal_name


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
