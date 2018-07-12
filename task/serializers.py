from .models import TypeTask, Task, Ecm
from rest_framework import serializers


class TypeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTask
        fields = ('id', 'name')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ('create_date', 'alter_date', 'system_prefix', 'is_active', 'survey_result', 'chat')


class EcmTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ecm
        exclude = ('create_date', 'alter_date', 'system_prefix', 'is_active')
