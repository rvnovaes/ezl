from .models import ServicePriceTable
from .serializers import ServicePriceTableSerializer
from rest_framework import viewsets, mixins


class ServicePriceTableViewSet(viewsets.ModelViewSet):
    """
    View responsável por listar os registros de Tabela de serviços de preços
    """
    queryset = ServicePriceTable.objects.all()
    serializer_class = ServicePriceTableSerializer
