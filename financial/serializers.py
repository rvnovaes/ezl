from .models import ServicePriceTable, CostCenter
from rest_framework import serializers
from .utils import valid_court_district, check_service_price_table_unique


class ServicePriceTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServicePriceTable
        exclude = ('system_prefix',)

    def validate(self, data):
        court_district = data.get('court_district')
        state = data.get('state')
        office_correspondent = data.get('office_correspondent')
        client = data.get('client')
        type_task = data.get('type_task')
        if court_district and state:
            if not valid_court_district(court_district, state):
                raise serializers.ValidationError("A Comarca selecionada não pertence à UF selecionada")
        if not check_service_price_table_unique(office_correspondent, state, court_district, type_task, client):
            raise serializers.ValidationError("Os campos office, office_correspondent, type_task, client, "
                                              "court_district, state devem criar um set único.")
        return data


class CostCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CostCenter
        exclude = ('system_prefix',)