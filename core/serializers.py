from django.db import transaction
from rest_framework import serializers
from pycpfcnpj import cpfcnpj
from .models import Person, Office, Company, Address, ContactMechanism
from .view_validators import create_person_office_relation, person_exists
from .messages import person_cpf_cnpj_already_exists, invalid_field
from .utils import get_office_session, get_office_api
from .validators import CpfCnpjOfficeUniqueValidator
from rest_framework.fields import SlugField
from rest_framework.compat import unicode_to_repr
from django.contrib.auth.models import User


class CreateUserDefault(object):
    def set_context(self, serializer_field):
        application = serializer_field.context['request'].auth.application
        if serializer_field.context['request'].user:
            self.create_user = serializer_field.context['request'].user
        else:
            self.create_user = application.user or application.office.create_user

    def __call__(self):
        return self.create_user

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class OfficeDefault(object):
    def set_context(self, serializer_field):
        self.office = serializer_field.context[
            'request'].auth.application.office

    def __call__(self):
        return self.office

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class CreateUserSerializerMixin(serializers.Serializer):
    create_user = serializers.HiddenField(default=CreateUserDefault())


class OfficeSerializerMixin(serializers.Serializer):
    office = serializers.HiddenField(default=OfficeDefault())


class PersonSerializer(serializers.ModelSerializer, CreateUserSerializerMixin):
    cpf_cnpj = SlugField(
        validators=[
            CpfCnpjOfficeUniqueValidator(queryset=Person.objects.filter())
        ],
        required=False)

    def create(self, validate_data):
        office_session = get_office_api(self.context.get('request'))
        person = super().create(validate_data)
        create_person_office_relation(person, person.create_user,
                                      office_session)
        return person

    def validate_cpf_cnpj(self, value):
        # https://github.com/matheuscas/pycpfcnpj
        if not cpfcnpj.validate(value):
            raise serializers.ValidationError(invalid_field('CPF/CNPJ'))
        return value

    class Meta:
        model = Person
        fields = ('id', 'name', 'legal_name', 'legal_type', 'cpf_cnpj',
                  'is_lawyer', 'is_customer', 'is_supplier', 'is_active',
                  'legacy_code', 'create_user')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'logo')
   

class OfficeSerializer(serializers.ModelSerializer):
    class Meta: 
        model  = Office
        fields = ('id', 'legal_name', 'name', 'is_active', 'logo', 'use_service', 'use_etl', 'cpf_cnpj')


class AddressSerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = Address        
        fields = '__all__'

    def get_city_name(self, obj):
        return obj.city.__str__()

    def get_state_name(self, obj):
        return obj.city.state.initials


class ContactMechanismSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ContactMechanism
        fields = '__all__'
