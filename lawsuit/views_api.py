from django.contrib.auth.mixins import LoginRequiredMixin
from .models import LawSuit, Movement, CourtDistrict, Folder, Instance, LawSuit, CourtDivision, TypeMovement, \
    Organ
from .serializers import CourtDistrictSerializer, FolderSerializer, InstanceSerializer, \
    LawSuitSerializer, CourtDivisionSerializer, MovementSerializer, TypeMovementSerializer, \
    OrganSerializer
from core.api import ApiViewMixin
from core.utils import get_office_session
from task.models import Task
from rest_framework import viewsets, mixins
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourtDistrictFilter, MovementFilter, LawsuitFilter, InstanceFilter
from rest_framework.decorators import permission_classes
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from core.models import CompanyUser, Company
from core.views import remove_invalid_registry


@permission_classes((TokenHasReadWriteScope, ))
class CourtDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourtDistrict.objects.all()
    serializer_class = CourtDistrictSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = CourtDistrictFilter
    search_fields = ('name', 'state__initials')


@permission_classes((TokenHasReadWriteScope, ))
class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    model = Folder

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office)


@permission_classes((TokenHasReadWriteScope, ))
class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
    model = Instance
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = InstanceFilter
    search_fields = ('name', 'legacy_code')

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office)


@permission_classes((TokenHasReadWriteScope, ))
class LawSuitViewSet(viewsets.ModelViewSet):
    queryset = LawSuit.objects.all()
    serializer_class = LawSuitSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = LawsuitFilter
    search_fields = ('folder__legacy_code',)
    model = LawSuit

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office)


class CompanyLawsuitViewSet(LawSuitViewSet):
    def get_queryset(self):
        if self.request.user.is_authenticated():
            return LawSuit.objects.filter(
                folder__person_customer__company__in=Company.objects.filter(
                    users__user=self.request.user))
        return []


def office_filter(queryset, request):
    office = get_office_session(request)
    return queryset.filter(office=office)


@permission_classes((TokenHasReadWriteScope, ))
class CourtDivisionViewSet(viewsets.ModelViewSet):
    queryset = CourtDivision.objects.all()
    serializer_class = CourtDivisionSerializer
    model = CourtDivision
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'legacy_code')


    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office)


@permission_classes((TokenHasReadWriteScope, ))
class MovementViewSet(viewsets.ModelViewSet):
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = MovementFilter
    search_fields = ('law_suit__legacycode', 'law_suit__law_suit_number',
                     'type_movement__legacycode')


@permission_classes((TokenHasReadWriteScope, ))
class TypeMovementViewSet(viewsets.ModelViewSet):
    queryset = TypeMovement.objects.all()
    serializer_class = TypeMovementSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )


@permission_classes((TokenHasReadWriteScope, ))
class OrganViewSet(viewsets.ModelViewSet):
    queryset = Organ.objects.all()
    serializer_class = OrganSerializer
    model = Organ
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('legal_name', 'legacy_code', 'court_district__state__initials', 'court_district__name')

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office)


# Não alterar view utilizada pela criacao de OS
class LawsuitApiView(LoginRequiredMixin, ApiViewMixin):
    model = LawSuit

    def filter_queryset(self, queryset):
        folder = self.request.GET.get('folder')
        if folder is None:
            raise self.bad_request("folder is required")

        queryset = queryset.filter(folder_id=folder)
        return office_filter(queryset, self.request)


# Não alterar view utilizada pela criacao de OS
class MovementApiView(LoginRequiredMixin, ApiViewMixin):
    model = Movement

    def filter_queryset(self, queryset):
        lawsuit = self.request.GET.get('lawsuit')
        if lawsuit is None:
            raise self.bad_request("lawsuit is required")

        queryset = queryset.filter(law_suit_id=lawsuit)
        return office_filter(queryset, self.request)


# Não alterar view utilizada pela criacao de OS
class TaskApiView(LoginRequiredMixin, ApiViewMixin):
    model = Task

    def filter_queryset(self, queryset):
        movement = self.request.GET.get('movement')
        if movement is None:
            raise self.bad_request("movement is required")

        queryset = queryset.filter(movement_id=movement)
        return office_filter(queryset, self.request)
