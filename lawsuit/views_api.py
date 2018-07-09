from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import LawSuit, Movement, CourtDistrict, Folder
from .serializers import CourtDistrictSerializer, FolderSerializer
from core.api import ApiViewMixin
from task.models import Task
from rest_framework import viewsets, mixins 


class CourtDistrictViewSet(viewsets.ModelViewSet):
    queryset = CourtDistrict.objects.all()
    serializer_class = CourtDistrictSerializer

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


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
