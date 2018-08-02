from .models import TypeTask, Task, Ecm
from .serializers import TypeTaskSerializer, TaskSerializer, TaskCreateSerializer, EcmTaskSerializer
from .filters import TaskApiFilter
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.decorators import permission_classes
from core.views_api import ApplicationView

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
