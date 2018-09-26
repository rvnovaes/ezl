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

    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(company__in=user.companys.all().values_list('company'))
