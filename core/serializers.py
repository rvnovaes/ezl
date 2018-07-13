from django.db import transaction
from rest_framework import serializers
from pycpfcnpj import cpfcnpj
from .models import Person
from .view_validators import create_person_office_relation, person_exists
from .messages import person_cpf_cnpj_already_exists, invalid_field
from .utils import get_office_session


class PersonSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        #TODO - Implementação para correta identificação do office da seção depende
        #da conclusão da tarefa EZL-873
        office_session = get_office_session(self.context['request'])
        with transaction.atomic():            
            if person_exists(validated_data['cpf_cnpj'], office_session):
                raise serializers.ValidationError(person_cpf_cnpj_already_exists())            
            person = super().create(validated_data)            
            create_person_office_relation(person, office_session.create_user, office_session)
            return person
    
    def validate_cpf_cnpj(self, value):
        #https://github.com/matheuscas/pycpfcnpj
        if not cpfcnpj.validate(value):
            raise serializers.ValidationError(invalid_field('CPF/CNPJ'))
        return value
    
    class Meta:
        model = Person
        fields = ('id', 'name', 'legal_name', 'legal_type', 'cpf_cnpj',
            'is_lawyer', 'is_customer', 'is_supplier', 'is_active', 'import_from_legacy',
            'auth_user', 'create_user', 'alter_user', 'legacy_code')
