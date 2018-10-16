from .models import TypeTask, Task, Ecm, TypeTaskMain
from rest_framework import serializers
from core.serializers import OfficeDefault, CreateUserDefault, CreateUserSerializerMixin, OfficeSerializerMixin


class TypeTaskMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTaskMain
        fields = ('id', 'name', 'is_hearing')


class TypeTaskSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):
    class Meta:
        model = TypeTask
        fields = ('id', 'name', 'type_task_main')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer,
                           CreateUserSerializerMixin, OfficeSerializerMixin):
    class Meta:
        model = Task
        exclude = ('create_date', 'alter_date', 'system_prefix', 'is_active',
                   'survey_result', 'chat', 'task_number')


class EcmTaskSerializer(serializers.ModelSerializer,
                        CreateUserSerializerMixin):
    class Meta:
        model = Ecm
        exclude = ('create_date', 'alter_date', 'system_prefix', 'is_active')
