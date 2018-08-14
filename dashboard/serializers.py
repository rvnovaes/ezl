from rest_framework import serializers
from .models import Dashboard, Card
from .utils import exec_code
from core.models import Company
from django.db import transaction


class CardSerializer(serializers.ModelSerializer):
	code = serializers.SerializerMethodField()
	class Meta: 
		model = Card
		fields = ('id', 'code')

	def get_code(self, obj):
		return exec_code(self, obj, 'code')


class DashboardSerializer(serializers.ModelSerializer):
	cards = CardSerializer(many=True, read_only=True)
	company_name = serializers.SerializerMethodField()

	class Meta:
		model = Dashboard
		fields = ('id', 'company', 'refresh', 'cards', 'company_name')

	def get_company_name(self, obj):
		return obj.company.name