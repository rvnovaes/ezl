from .models import ServicePriceTable, CostCenter
from .serializers import ServicePriceTableSerializer, CostCenterSerializer
from rest_framework import viewsets, mixins
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.decorators import permission_classes


@permission_classes((TokenHasReadWriteScope,))
class ServicePriceTableViewSet(viewsets.ModelViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = ServicePriceTable.objects.all().order_by('office', 'office_correspondent')
    serializer_class = ServicePriceTableSerializer


@permission_classes((TokenHasReadWriteScope,))
class CostCenterViewSet(viewsets.ModelViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
