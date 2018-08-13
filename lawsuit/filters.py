from .models import CourtDistrict, State, Movement
import django_filters
from django_filters import rest_framework as filters 


class CourtDistrictFilter(filters.FilterSet):
	state = filters.CharFilter(name="state__initials", lookup_expr='iexact')
	name = filters.CharFilter(name='name', lookup_expr='icontains')
	class Meta: 
		model = CourtDistrict
		fields = ['state', 'name']


class MovementFilter(filters.FilterSet):
	legacycode = filters.CharFilter(name='legacy_code', lookup_expr='iexact')
	law_suit_number = filters.CharFilter(name='law_suit__law_suit_number', lookup_expr='iexact')	
	type_movement_legacy_code = filters.CharFilter(name='type_movement__legacy_code', lookup_expr='iexact')
	
	class Meta:
		model = Movement
		fields = ['legacycode', 'law_suit_number', 'type_movement_legacy_code']