from rest_framework import serializers
from .models import Dashboard, Card, DashboardCard
from .utils import exec_code
from core.models import Company
from django.db import transaction


class DashboardCardSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()

    class Meta:
        model = DashboardCard
        fields = ('sequence', 'code')

    def get_code(self, obj):
        return exec_code(self, obj.card, 'code')


class DashboardSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    dashboardcard_set = DashboardCardSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ('id', 'company', 'logo', 'refresh', 
                  'company_name', 'dashboardcard_set')

    def get_company_name(self, obj):
        return obj.company.name
