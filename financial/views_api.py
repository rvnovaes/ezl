from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import ServicePriceTable
from .serializers import ServicePriceTableSerializer
from core.api import ApiViewMixin
from task.models import Task
from rest_framework import viewsets, mixins 
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


class ServicePriceTableViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View responsável por listar os registros de Tabela de serviços de preços
    """
    queryset = ServicePriceTable.objects.all()
    serializer_class = ServicePriceTableSerializer
