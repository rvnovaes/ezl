from .models import CourtDistrict, Folder, Instance
from rest_framework import serializers


class CourtDistrictSerializer(serializers.ModelSerializer):
	class Meta:
		model = CourtDistrict
		fields = ('id', 'name', 'state')


class FolderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Folder
		fields = ('id', 'folder_number', 'person_customer', 'cost_center', 'office', 'create_user')


class InstanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Instance
		fields = ('id', 'name', 'office', 'create_user', 'legacy_code')