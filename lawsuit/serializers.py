from .models import CourtDistrict
from rest_framework import serializers



class CourtDistrictSerializer(serializers.ModelSerializer):
	class Meta:
		model = CourtDistrict
		fields = ('id', 'name', 'state')