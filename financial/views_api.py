from .models import ServicePriceTable
from .serializers import ServicePriceTableSerializer
from rest_framework import viewsets, mixins


class ServicePriceTableViewSet(viewsets.ModelViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = ServicePriceTable.objects.all().order_by('office', 'office_correspondent')
    serializer_class = ServicePriceTableSerializer
