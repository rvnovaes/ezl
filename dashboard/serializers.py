from rest_framework import serializers
from .models import Dashboard, Card
from core.models import Company

class CardSerializer(serializers.ModelSerializer):
	value = serializers.SerializerMethodField()
	class Meta: 
		model = Card
		fields = ('id', 'title', 'subtitle', 'value')

	def get_value(self, obj):	
		try:			
			company = Company.objects.first() # Todo: Ajustar		
			exec(obj.value)
			return locals().get('value')
		except:
			return ''



class DashboardSerializer(serializers.ModelSerializer):
	cards = CardSerializer(many=True, read_only=True)
	class Meta:
		model = Dashboard
		fields = ('id', 'company', 'cards')