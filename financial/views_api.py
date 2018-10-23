from .models import ServicePriceTable, CostCenter
from .serializers import ServicePriceTableSerializer, CostCenterSerializer
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework.decorators import permission_classes
from core.views_api import OfficeMixinViewSet


@permission_classes((TokenHasReadWriteScope,))
class ServicePriceTableViewSet(OfficeMixinViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = ServicePriceTable.objects.all().order_by('office', 'office_correspondent')
    serializer_class = ServicePriceTableSerializer


@permission_classes((TokenHasReadWriteScope,))
class CostCenterViewSet(OfficeMixinViewSet):
    """
    Permite a manutenção do cadastro de Tabela de preços de serviços
    """
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
