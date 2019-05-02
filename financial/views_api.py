from .models import ServicePriceTable, CostCenter, PolicyPrice
from .serializers import ServicePriceTableSerializer, CostCenterSerializer, PolicyPriceSerializer
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
    Permite a manutenção do cadastro de Centros de custo
    """
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer


@permission_classes((TokenHasReadWriteScope,))
class PolicyPriceViewSet(OfficeMixinViewSet):
    """
    Permite a manutenção do cadastro de Tipos de preços
    """
    queryset = PolicyPrice.objects.all()
    serializer_class = PolicyPriceSerializer
