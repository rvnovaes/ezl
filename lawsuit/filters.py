from .models import CourtDistrict, State
import django_filters
from django_filters import rest_framework as filters 


class CourtDistrictFilter(filters.FilterSet):
	state = filters.CharFilter(name="state__initials", lookup_expr='iexact')
	name = filters.CharFilter(name='name', lookup_expr='icontains')
	class Meta: 
		model = CourtDistrict