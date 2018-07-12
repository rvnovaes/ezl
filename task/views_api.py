from .models import TypeTask, Task, Ecm
from .serializers import TypeTaskSerializer, TaskSerializer, EcmTaskSerializer
from rest_framework import viewsets
from rest_framework.filters import SearchFilter


class TypeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypeTask.objects.filter(is_active=True, simple_service=True)
    serializer_class = TypeTaskSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class EcmTaskViewSet(viewsets.ModelViewSet):
    queryset = Ecm.objects.all()
    serializer_class = EcmTaskSerializer
