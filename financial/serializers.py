from .models import ServicePriceTable, CostCenter, PolicyPrice, BillingMoment
from rest_framework import serializers
from .utils import valid_court_district, check_service_price_table_unique, check_office_correspondent_relation
from core.serializers import CreateUserSerializerMixin, OfficeSerializerMixin, OfficeSerializer, PersonSerializer
from lawsuit.serializers import CourtDistrictSerializer, CourtDistrictComplementSerializer
from task.serializers import TypeTaskSerializer

class PolicyPriceSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin): 
    class Meta: 
        model = PolicyPrice
        fields = '__all__'


class ServicePriceTableSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):
    policy_price = PolicyPriceSerializer(many=False, read_only=True)
    office_correspondent = OfficeSerializer(many=False, read_only=True)
    type_task = TypeTaskSerializer(many=False, read_only=True)
    office_network = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    court_district = CourtDistrictSerializer(many=False, read_only=True)
    court_district_complement = CourtDistrictComplementSerializer(many=False, read_only=True)
    city = serializers.SerializerMethodField()
    client = PersonSerializer(many=False, read_only=True)
    office_rating = serializers.SerializerMethodField()
    office_return_rating = serializers.SerializerMethodField()

    class Meta:
        model = ServicePriceTable
        exclude = ('system_prefix', 'create_date', 'alter_date', 'alter_user')

    def get_office_network(self, obj):
        return obj.office_network.name if obj.office_network else ''

    def get_state(self, obj):
        return obj.state.initials if obj.state else None

    def get_city(self, obj): 
        return obj.city.name if obj.city else None

    def get_office_rating(self, obj):
        return obj.office_rating

    def get_office_return_rating(self, obj):
        return obj.office_return_rating

    def validate(self, data):
        pk = self.instance.id if self.instance else None
        office = data.get('office')
        court_district = data.get('court_district')
        court_dictrict_complement = data.get('court_district_complement')
        state = data.get('state')
        office_correspondent = data.get('office_correspondent')
        client = data.get('client')
        type_task = data.get('type_task')
        if office_correspondent:
            if not check_office_correspondent_relation(office, office_correspondent):
                raise serializers.ValidationError("O escritório correspondente informado não possui relacionamento com "
                                                  "o escritório da sessão")
        if court_district and state:
            if not valid_court_district(court_district, state):
                raise serializers.ValidationError("A Comarca selecionada não pertence à UF selecionada")
        if not check_service_price_table_unique(pk, office, office_correspondent, state, court_district, type_task,
                                                client, court_dictrict_complement):
            raise serializers.ValidationError("Os campos office, office_correspondent, type_task, client, "
                                              "court_district, state e court_district_complement devem criar "
                                              "um set único.")
        return data


class CostCenterSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):

    class Meta:
        model = CostCenter
        exclude = ('system_prefix', 'create_date', 'alter_date', 'alter_user')
