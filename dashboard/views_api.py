from rest_framework import viewsets
from .models import Dashboard
from .serializers import DashboardSerializer
from django_filters.rest_framework import DjangoFilterBackend


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('company_id', )
