from .models import TypeTask
from rest_framework import serializers


class TypeTaskSerializer(serializers.ModelSerializer):
	class Meta: 
		model = TypeTask
		fields = ('id', 'name')