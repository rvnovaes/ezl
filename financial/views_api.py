from .models import ServicePriceTable, CostCenter
from .serializers import ServicePriceTableSerializer, CostCenterSerializer
from rest_framework import viewsets, mixins


class ServicePriceTableViewSet(viewsets.ModelViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = ServicePriceTable.objects.all().order_by('office', 'office_correspondent')
    serializer_class = ServicePriceTableSerializer


class CostCenterViewSet(viewsets.ModelViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
