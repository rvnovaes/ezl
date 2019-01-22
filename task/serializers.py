from .models import TypeTask, Task, Ecm, TypeTaskMain
from rest_framework import serializers
from core.models import Person, Office
from core.serializers import OfficeDefault, CreateUserDefault, CreateUserSerializerMixin, OfficeSerializerMixin
from rest_framework.compat import unicode_to_repr


class PersonAskedByDefault(object):
    def set_context(self, serializer_field):
        try:
            self.person_asked_by = serializer_field.context[
                'request'].auth.application.user.person
        except:
            self.person_asked_by = None

    def __call__(self):
        return self.person_asked_by

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class TypeTaskMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTaskMain
        fields = ('id', 'name', 'is_hearing')


class TypeTaskSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):
    class Meta:
        model = TypeTask
        fields = ('id', 'name', 'type_task_main', 'legacy_code', 'create_user', 'office')


class TaskSerializer(serializers.ModelSerializer, CreateUserSerializerMixin, OfficeSerializerMixin):

    person_asked_by = serializers.HiddenField(default=PersonAskedByDefault())

    class Meta:
        model = Task
        exclude = ('create_date', 'alter_date', 'system_prefix', 'survey_result', 'chat', 'company_chat', 'task_hash')

    def validate_person_asked_by(self, value):
        if not value:
            raise serializers.ValidationError("O escritório da sessão não possui um usuário padrão. "
                                              "Entre em contato com o suporte")
        return value

    def validate_legacy_code(self, value):
        office = self.fields['office'].get_default()
        if Task.objects.filter(office=office, legacy_code=value):
            raise serializers.ValidationError("O legacy_code informado já está sendo utilizado neste escritório")
        return value


class TaskCreateSerializer(TaskSerializer):

    class Meta:
        model = Task
        fields = ('final_deadline_date', 'performance_place', 'movement', 'type_task', 'description', 'task_status',
                  'legacy_code', 'requested_date', 'create_user', 'office', 'task_hash')


class EcmTaskSerializer(serializers.ModelSerializer,
                        CreateUserSerializerMixin):
    class Meta:
        model = Ecm
        exclude = ('create_date', 'alter_date', 'system_prefix', 'is_active')


class OfficeToPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('pk', 'legal_name')


class TaskToPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('pk', 'amount', 'parent')


class TaskCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('pk', 'task_number', 'final_deadline_date', 'executed_by_checkin', 'company_representative_checkin')
