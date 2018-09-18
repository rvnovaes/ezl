from rest_framework import serializers
from .models import Dashboard, Card, DashboardCard, DashboardDoughnutChart, \
    DashboardLineChart
from .utils import exec_code
from core.models import Company
from django.db import transaction


class DashboardComponentSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()

    class Meta:
        fields = ('sequence', 'code')


class DashboardCardSerializer(DashboardComponentSerializer):
    class Meta(DashboardComponentSerializer.Meta):
        model = DashboardCard

    def get_code(self, obj):
        return exec_code(self, obj.card, 'code')


class DashboardDoughnutChartSerializer(DashboardComponentSerializer):
    class Meta(DashboardComponentSerializer.Meta):
        model = DashboardDoughnutChart

    def get_code(self, obj):
        return exec_code(self, obj.doughnut_chart, 'code')


class DashboardLineChartSerializer(DashboardComponentSerializer):
    class Meta(DashboardComponentSerializer.Meta):
        model = DashboardLineChart

    def get_code(self, obj):
        return exec_code(self, obj.line_chart, 'code')


class DashboardSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    dashboardcard_set = DashboardCardSerializer(many=True, read_only=True)
    dashboarddoughnutchart_set = DashboardDoughnutChartSerializer(
        many=True, read_only=True)
    dashboardlinechart_set = DashboardLineChartSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ('id', 'company', 'logo', 'refresh', 'company_name',
                  'dashboardcard_set', 'dashboarddoughnutchart_set',
                  'dashboardlinechart_set')

    def get_company_name(self, obj):
        return obj.company.name
