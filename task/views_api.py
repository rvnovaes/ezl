from .models import TypeTask, Task, Ecm, TypeTaskMain
from .serializers import TypeTaskSerializer, TaskSerializer, TaskCreateSerializer, EcmTaskSerializer, \
    TypeTaskMainSerializer
from .filters import TaskApiFilter, TypeTaskMainFilter
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.decorators import permission_classes
from core.views_api import ApplicationView
from lawsuit.models import Folder, Movement
from django.utils import timezone
from django.db.models import Q
from core.views_api import OfficeMixinViewSet


@permission_classes((TokenHasReadWriteScope,))
class TypeTaskMainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypeTaskMain.objects.all()
    serializer_class = TypeTaskMainSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = TypeTaskMainFilter
    search_fields = ('name', )


@permission_classes((TokenHasReadWriteScope, ))
class TypeTaskViewSet(OfficeMixinViewSet):
    queryset = TypeTask.objects.filter(is_active=True)
    serializer_class = TypeTaskSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', 'legacy_code')


@permission_classes((TokenHasReadWriteScope, ))
class EcmTaskViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Ecm.objects.all()
    serializer_class = EcmTaskSerializer

    def get_queryset(self, *args, **kwargs):
        office = self.request.auth.application.office
        return self.queryset.filter(Q(tasks__office=office.id) | Q(task__office_id=office.id))


@permission_classes((TokenHasReadWriteScope, ))
class TaskViewSet(OfficeMixinViewSet, ApplicationView):
    queryset = Task.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = TaskApiFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer
        return TaskSerializer


@api_view(['GET'])
@permission_classes((TokenHasReadWriteScope, ))
def list_audience_totals(request):
    company = request.auth.application.company
    audience = {}
    if company.users.filter(user=request.user).exists():
        folders = Folder.objects.filter(person_customer__company=company)
        tasks = Task.objects.filter(movement__folder__in=folders)
        audiences = tasks.filter(type_task__is_audience=True)
        audiences_this_month = audiences.filter(
            final_deadline_date__year=timezone.now().year,
            final_deadline_date__month=timezone.now().month)
        agreement_this_month = audiences_this_month.filter(
            **{'survey_result__Acordo realizado?': 'Sim'})
        audiences_this_week = audiences_this_month.filter(
            final_deadline_date__week=timezone.now().isocalendar()[1])
        audience['total_audience'] = audiences.count()
        audience['total_audience_this_month'] = audiences_this_month.count()
        audience['total_audience_this_week'] = audiences_this_week.count()
        audience['agreement_this_month'] = agreement_this_month.count()
    return Response(audience)
