from .models import TypeTask, Task, Ecm, TypeTaskMain
from rest_framework import serializers
from core.models import Person, Office
from core.serializers import OfficeDefault, CreateUserDefault, CreateUserSerializerMixin, OfficeSerializerMixin
from rest_framework.compat import unicode_to_repr
from rest_framework.pagination import PageNumberPagination
from task.utils import validate_final_deadline_date
from task.messages import min_hour_error
from manager.utils import get_template_value_value
from manager.enums import TemplateKeys


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
    office_name = serializers.SerializerMethodField()
    executed_by_name = serializers.SerializerMethodField()
    type_task_name = serializers.SerializerMethodField()
    law_suit_number = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    court_district_name = serializers.SerializerMethodField()
    external_url = serializers.SerializerMethodField()

    class Meta:
        model = Task
        exclude = ('alter_date', 'system_prefix', 'survey_result', 'chat', 'company_chat', 'task_hash')
    
    def get_office_name(self, obj):
        return obj.office.legal_name

    def get_executed_by_name(self, obj):
        if obj.get_child: 
            return obj.get_child.office.legal_name            
        return obj.person_executed_by.legal_name if obj.person_executed_by else ''

    def get_type_task_name(self, obj):
        return obj.type_task.name

    def get_law_suit_number(self, obj): 
        return obj.lawsuit_number or ''

    def get_state(self, obj):
        return obj.court_district.state.initials if obj.court_district else ''
    
    def get_court_district_name(self, obj): 
        return obj.court_district.name if obj.court_district else ''

    def validate_person_asked_by(self, value):
        if not value:
            raise serializers.ValidationError("O escritório da sessão não possui um usuário padrão. "
                                              "Entre em contato com o suporte")
        return value

    def get_external_url(self, obj):
        return 'providencias/external-task-detail/' + obj.task_hash.hex

    def validate_legacy_code(self, value):
        office = self.fields['office'].get_default()
        if Task.objects.filter(office=office, legacy_code=value):
            raise serializers.ValidationError("O legacy_code informado já está sendo utilizado neste escritório")
        return value

    def validate_final_deadline_date(self, obj):
        office = self.fields['office'].get_default()
        if not validate_final_deadline_date(obj, office):
            min_hour = get_template_value_value(office, TemplateKeys.MIN_HOUR_OS.name)
            raise serializers.ValidationError(min_hour_error(min_hour))
        return obj


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
    date_executed_by_checkin = serializers.SerializerMethodField()
    task_company_representative = serializers.SerializerMethodField()
    date_company_representative_checkin = serializers.SerializerMethodField()
    os_executor = serializers.SerializerMethodField()
    law_suit_number = serializers.SerializerMethodField()
    person_customer = serializers.SerializerMethodField()
    type_task_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        depth = 0
        fields = ('pk', 'task_number', 'type_task_name', 'final_deadline_date',
                  'os_executor', 'date_executed_by_checkin',
                  'task_company_representative', 'date_company_representative_checkin',
                  'law_suit_number', 'person_customer')

    def get_date_executed_by_checkin(self, obj):
        return obj.executed_by_checkin.date if obj.executed_by_checkin else None

    def get_task_company_representative(self, obj):
        return obj.company_representative_checkin.create_user.person.legal_name if obj.company_representative_checkin \
            else None

    def get_date_company_representative_checkin(self, obj):
        return obj.company_representative_checkin.date if obj.company_representative_checkin else None

    def get_os_executor(self, obj):
        return obj.os_executor

    def get_law_suit_number(self, obj):
        return obj.lawsuit_number

    def get_person_customer(self, obj):
        return obj.movement.law_suit.folder.person_customer.legal_name

    def get_type_task_name(self, obj):
        return obj.type_task.name


class CustomResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
