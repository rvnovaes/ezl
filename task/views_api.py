from .models import TypeTask
from .serializers import TypeTaskSerializer
from rest_framework import viewsets
from rest_framework.filters import SearchFilter


class TypeTaskViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = TypeTask.objects.filter(is_active=True, simple_service=True)
	serializer_class = TypeTaskSerializer
	filter_backends = (SearchFilter,)
	search_fields = ('name',)