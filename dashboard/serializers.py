from rest_framework import serializers
from .models import Dashboard, Card
from .utils import exec_code
from core.models import Company
from django.db import transaction


class CardSerializer(serializers.ModelSerializer):
	value = serializers.SerializerMethodField()
	percent = serializers.SerializerMethodField()
	class Meta: 
		model = Card
		fields = ('id', 'title', 'subtitle', 'value', 'percent')


	def get_value(self, obj):	
		return exec_code(self, obj, 'value')

	def get_percent(self, obj):				
		return exec_code(self, obj, 'percent')


class DashboardSerializer(serializers.ModelSerializer):
	cards = CardSerializer(many=True, read_only=True)
	class Meta:
		model = Dashboard
		fields = ('id', 'company', 'cards')