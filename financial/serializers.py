from .models import ServicePriceTable
from lawsuit.models import CourtDistrict
from core.models import State
from rest_framework import serializers
from .utils import valid_court_district


class ServicePriceTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServicePriceTable
        exclude = ('system_prefix',)

    def validate(self, data):
        court_district = data.get('court_district')
        state = data.get('state')
        if court_district and state:
            if not valid_court_district(court_district, state):
                raise serializers.ValidationError("A Comarca selecionada não pertence à UF selecionada")
        return data
