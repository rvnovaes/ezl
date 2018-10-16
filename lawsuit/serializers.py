from .models import CourtDistrict, Folder, Instance, LawSuit, CourtDivision, \
    TypeMovement, Movement, Organ
from rest_framework import serializers
from core.serializers import OfficeDefault, CreateUserDefault, CreateUserSerializerMixin, OfficeSerializerMixin


class CourtDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtDistrict
        fields = ('id', 'name', 'state')


class FolderSerializer(serializers.ModelSerializer, CreateUserSerializerMixin,
                       OfficeSerializerMixin):
    class Meta:
        model = Folder
        fields = ('id', 'office', 'folder_number', 'person_customer',
                  'cost_center', 'office', 'create_user', 'legacy_code')

    def validate_legacy_code(self, value):
        if not value:
            value = ""
        return value


class InstanceSerializer(serializers.ModelSerializer, CreateUserSerializerMixin,
                       OfficeSerializerMixin):
    class Meta:
        model = Instance
        fields = ('id', 'name', 'office', 'create_user', 'legacy_code')


class LawSuitSerializer(serializers.ModelSerializer, CreateUserSerializerMixin,
                        OfficeSerializerMixin):
    office_name = serializers.SerializerMethodField()

    class Meta:
        model = LawSuit
        fields = ('id', 'folder', 'law_suit_number', 'opposing_party',
                  'court_district', 'instance', 'organ', 'court_division',
                  'person_lawyer', 'is_current_instance', 'is_active',
                  'office', 'create_user', 'legacy_code', 'office_name')

    def get_office_name(self, obj):
        return obj.office.legal_name


class CourtDivisionSerializer(serializers.ModelSerializer, CreateUserSerializerMixin,
                              OfficeSerializerMixin):
    class Meta:
        model = CourtDivision
        fields = ('id', 'name', 'office', 'create_user', 'legacy_code')


class TypeMovementSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):
    class Meta:
        model = TypeMovement
        fields = ('id', 'office', 'name', 'legacy_code', 'create_user')


class MovementSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):

    law_suit = serializers.PrimaryKeyRelatedField(allow_null=False, label='Processo', queryset=LawSuit.objects.all(),
                                                  required=True)

    class Meta:
        model = Movement
        fields = ('id', 'type_movement', 'law_suit', 'folder', 'legacy_code', 'office', 'create_user')


class OrganSerializer(serializers.ModelSerializer, CreateUserSerializerMixin,
                      OfficeSerializerMixin):
    class Meta:
        model = Organ
        fields = ('id', 'legal_name', 'name', 'cpf_cnpj', 'court_district', 'is_active', 'legacy_code', 'office',
                  'create_user')
