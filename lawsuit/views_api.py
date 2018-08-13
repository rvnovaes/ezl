from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import LawSuit, Movement, CourtDistrict, Folder, Instance, LawSuit, CourtDivision, TypeMovement, \
    Organ
from .serializers import CourtDistrictSerializer, FolderSerializer, InstanceSerializer, \
    LawSuitSerializer, CourtDivisionSerializer, MovementSerializer, TypeMovementSerializer, \
    OrganSerializer
from core.api import ApiViewMixin
from task.models import Task
from rest_framework import viewsets, mixins
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourtDistrictFilter, MovementFilter
from rest_framework.decorators import permission_classes
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope


@permission_classes((TokenHasReadWriteScope,))
class CourtDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourtDistrict.objects.all()
    serializer_class = CourtDistrictSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = CourtDistrictFilter
    search_fields = ('name', 'state__initials')


@permission_classes((TokenHasReadWriteScope,))
class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(office=self.request.auth.application.office)


@permission_classes((TokenHasReadWriteScope,))
class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer


@permission_classes((TokenHasReadWriteScope,))
class LawSuitViewSet(viewsets.ModelViewSet):
    serializer_class = LawSuitSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('folder__legacy_code',)

    def get_queryset(self):
        return LawSuit.objects.filter(office=self.request.auth.application.office)


@permission_classes((TokenHasReadWriteScope,))
class CourtDivisionViewSet(viewsets.ModelViewSet):
    queryset = CourtDivision.objects.all()
    serializer_class = CourtDivisionSerializer


@permission_classes((TokenHasReadWriteScope,))
class MovementViewSet(viewsets.ModelViewSet):
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = MovementFilter
    search_fields = ('law_suit__legacycode', 'law_suit__law_suit_number', 'type_movement__legacycode')


@permission_classes((TokenHasReadWriteScope,))
class TypeMovementViewSet(viewsets.ModelViewSet):
    queryset = TypeMovement.objects.all()
    serializer_class = TypeMovementSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


@permission_classes((TokenHasReadWriteScope,))
class OrganViewSet(viewsets.ModelViewSet):
    queryset = Organ.objects.all()
    serializer_class = OrganSerializer


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
