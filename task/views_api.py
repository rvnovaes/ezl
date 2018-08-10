from .models import TypeTask, Task, Ecm
from .serializers import TypeTaskSerializer, TaskSerializer, TaskCreateSerializer, EcmTaskSerializer
from .filters import TaskApiFilter
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.decorators import permission_classes
from core.views_api import ApplicationView
from lawsuit.models import Folder, Movement
from django.utils import timezone


@permission_classes((TokenHasReadWriteScope,))
class TypeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypeTask.objects.filter(is_active=True, simple_service=True)
    serializer_class = TypeTaskSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


@permission_classes((TokenHasReadWriteScope,))
class EcmTaskViewSet(viewsets.ModelViewSet):
    queryset = Ecm.objects.all()
    serializer_class = EcmTaskSerializer

@permission_classes((TokenHasReadWriteScope,))
class TaskViewSet(viewsets.ModelViewSet, ApplicationView):
    queryset = Task.objects.all()    
    filter_backends = (DjangoFilterBackend,)
    filter_class = TaskApiFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer
        return TaskSerializer

@api_view(['GET'])
@permission_classes((TokenHasReadWriteScope,))
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
        audiences_this_week = audiences_this_month.filter(
            final_deadline_date__week=timezone.now().isocalendar()[1])        
        audience['total_audience'] = audiences.count()
        audience['total_audience_this_month'] = audiences_this_month.count()
        audience['total_audience_this_week'] = audiences_this_week.count()
    return Response(audience)

# @api_view
# @permission_classes((TokenHasReadWriteScope,))
# def list