from rest_framework import serializers
from .models import BillingDetails
from core.serializers import AddressSerializer


class BillingDetailSerializer(serializers.ModelSerializer):
    billing_address = AddressSerializer(many=False)

    class Meta:
        model = BillingDetails
        fields = '__all__'
