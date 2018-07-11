from .models import CourtDistrict, Folder, Instance, LawSuit, CourtDivision,\
	TypeMovement, Movement
from rest_framework import serializers


class CourtDistrictSerializer(serializers.ModelSerializer):
	class Meta:
		model = CourtDistrict
		fields = ('id', 'name', 'state')


class FolderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Folder
		fields = ('id', 'office', 'folder_number', 'person_customer', 'cost_center', 'office', 'create_user', 'legacy_code')


class InstanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Instance
		fields = ('id', 'name', 'office', 'create_user', 'legacy_code')


class LawSuitSerializer(serializers.ModelSerializer):
	class Meta:
		model = LawSuit
		fields = ('id', 'folder', 'law_suit_number', 'opposing_party', 'court_district',
			'instance', 'organ', 'court_division', 'person_lawyer', 'is_current_instance',
			'is_active', 'office', 'create_user', 'legacy_code')


class CourtDivisionSerializer(serializers.ModelSerializer):
	class Meta:
		model = CourtDivision
		fields = ('id', 'name', 'office', 'create_user', 'legacy_code')


class TypeMovementSerializer(serializers.ModelSerializer):
	class Meta:
		model = TypeMovement
		fields = ('id', 'office', 'name', 'uses_wo', 'legacy_code', 'create_user')


class MovementSerializer(serializers.ModelSerializer):
	class Meta:
		model = Movement
		fields = ('id', 'type_movement', 'law_suit', 'folder', 'office', 'create_user', 'legacy_code')