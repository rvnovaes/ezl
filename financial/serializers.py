from .models import ServicePriceTable
from rest_framework import serializers


class ServicePriceTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePriceTable
        exclude = ('system_prefix',)
