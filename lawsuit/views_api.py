from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import LawSuit, Movement, CourtDistrict, Folder, Instance, LawSuit, CourtDivision, TypeMovement
from .serializers import CourtDistrictSerializer, FolderSerializer, InstanceSerializer, \
    LawSuitSerializer, CourtDivisionSerializer, MovementSerializer, TypeMovementSerializer
from core.api import ApiViewMixin
from task.models import Task
from rest_framework import viewsets, mixins
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourtDistrictFilter, MovementFilter


class CourtDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourtDistrict.objects.all()
    serializer_class = CourtDistrictSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = CourtDistrictFilter
    search_fields = ('name', 'state__initials')


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class InstanceViewSet(viewsets.ModelViewSet):
    """
		Permite a manutenção do cadatro de Instâncias
	"""
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer


class LawSuitViewSet(viewsets.ModelViewSet):
    """
		Permite a manutenção do cadatro de Processos
	"""
    queryset = LawSuit.objects.all()
    serializer_class = LawSuitSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('folder__legacycode',)


class CourtDivisionViewSet(viewsets.ModelViewSet):
    """
        Permite a manutenção do cadastro de Varas
    """
    queryset = CourtDivision.objects.all()
    serializer_class = CourtDivisionSerializer


class MovementViewSet(viewsets.ModelViewSet):
    """
        Permite a manutenção do cadastro de Movimentações        
    """
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = MovementFilter
    search_fields = ('law_suit__legacycode', 'law_suit__law_suit_number', 'type_movement__legacycode')


class TypeMovementViewSet(viewsets.ModelViewSet):
    queryset = TypeMovement.objects.all()
    serializer_class = TypeMovementSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


# Todo: Alterar para rest-framework
class LawsuitApiView(LoginRequiredMixin, ApiViewMixin):
    model = LawSuit

    def filter_queryset(self, queryset):
        folder = self.request.GET.get('folder')
        if folder is None:
            raise self.bad_request("folder is required")

        queryset = queryset.filter(folder_id=folder)
        return queryset


class MovementApiView(LoginRequiredMixin, ApiViewMixin):
    model = Movement

    def filter_queryset(self, queryset):
        lawsuit = self.request.GET.get('lawsuit')
        if lawsuit is None:
            raise self.bad_request("lawsuit is required")

        queryset = queryset.filter(law_suit_id=lawsuit)
        return queryset


class TaskApiView(LoginRequiredMixin, ApiViewMixin):
    model = Task

    def filter_queryset(self, queryset):
        movement = self.request.GET.get('movement')
        if movement is None:
            raise self.bad_request("movement is required")

        queryset = queryset.filter(movement_id=movement)
        return queryset
