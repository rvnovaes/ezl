from django.forms import Select, Textarea, RadioSelect
from django_filters import FilterSet, ModelChoiceFilter, NumberFilter, CharFilter, ChoiceFilter, MultipleChoiceFilter, \
    BooleanFilter, ModelMultipleChoiceFilter
from dal import autocomplete
from django.db.models import Q
from core.models import Person, State, Office, Team
from core.utils import filter_valid_choice_form
from core.widgets import MDDateTimeRangeFilter, TypeaHeadForeignKeyWidget
from financial.models import CostCenter
from lawsuit.models import CourtDistrict, Organ, CourtDistrictComplement
from task.models import TypeTask, Task, Filter, TaskStatus
from .models import DashboardViewModel, TypeTaskMain
from core.utils import get_office_session
from task.utils import get_status_to_filter
from django import forms

from django_filters import rest_framework as filters

OFFICE = 'E'
CLIENT = 'C'
GROUP_BY_TASK_TO_PAY_TYPE = (
    (OFFICE, 'Por Escritório Correspondente'),
    (CLIENT, 'Por Cliente'),
)

GROUP_BY_TASK_TO_RECEIVE_TYPE = (
    (OFFICE, 'Por Escritório Contratante'),
    (CLIENT, 'Por Cliente'),
)


class TaskApiFilter(FilterSet):
    class Meta:
        model = Task
        fields = ['legacy_code', 'task_number']


class TaskFilter(FilterSet):
    state = ModelMultipleChoiceFilter(
        queryset=filter_valid_choice_form(
            State.objects.filter(is_active=True)),
        label="UF",
        widget=autocomplete.ModelSelect2Multiple(url='state-autocomplete'))
    court_district = ModelMultipleChoiceFilter(
        queryset=filter_valid_choice_form(CourtDistrict.objects.filter(is_active=True)),
        label='Comarca',
        widget=autocomplete.ModelSelect2Multiple(url='courtdistrict_select2', forward=['state']))
    court_district_complement = CharFilter(
        label="Complemento de Comarca",
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=CourtDistrictComplement,
            field_related='name',
            forward='court_district',
            name='court_district_complement',
            url='/processos/typeahead/search/complemento',))
    task_status = MultipleChoiceFilter(
        label="Status",
        required=False,
        choices=[(task_status.name, task_status.value)
                 for task_status in TaskStatus])
    type_task = ModelMultipleChoiceFilter(
        queryset=TypeTask.objects.filter(is_active=True),
        label='Tipo de Serviço',
        widget=autocomplete.ModelSelect2Multiple(url='type-task-autocomplete'))
    type_task_main = ModelMultipleChoiceFilter(
        queryset=TypeTaskMain.objects.all(),
        label='Tipo de Serviço Principal',
        widget=autocomplete.ModelSelect2Multiple(url='type-task-main-autocomplete'))    
    cost_center = ModelChoiceFilter(
        queryset=filter_valid_choice_form(
            CostCenter.objects.filter(is_active=True)),
        label="Setor")
    court = ModelChoiceFilter(
        queryset=filter_valid_choice_form(
            Organ.objects.filter(is_active=True)),
        label="Órgão")
    team = ModelChoiceFilter(
        queryset=filter_valid_choice_form(Team.objects.filter(is_active=True)),
        label="Equipe")
    folder_number = NumberFilter(label=u"Nº da pasta")
    folder_legacy_code = CharFilter(label=u"Nº da pasta de origem")
    law_suit_number = CharFilter(label=u"Nº do processo")
    task_number = NumberFilter(label=u"Nº da OS")
    task_legacy_code = CharFilter(label=u"Nº da OS de origem")
    task_origin_code = NumberFilter(label=u"Nº da OS de origem")
    client = ModelMultipleChoiceFilter(
        queryset=Person.objects.filter(is_active=True, is_customer=True),
        label='Cliente',
        widget=autocomplete.ModelSelect2Multiple(url='get_client_2'))
    office_executed_by = CharFilter(
        label='Escritório contratado',
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Office,
            field_related='legal_name',
            name='office_executed_by',
            url='/office_correspondent_form'))
    person_executed_by = CharFilter(
        label="Correspondente",
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Person,
            field_related='legal_name',
            name='person_executed_by',
            url='/correspondent_form'))
    person_asked_by = CharFilter(
        label="Solicitante",
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Person,
            field_related='legal_name',
            name='person_asked_by',
            url='/requester_form'))
    origin_office_asked_by = CharFilter(
        label="Solicitante de origem",
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Office,
            field_related='legal_name',
            name='origin_office_asked_by',
            url='/origin_requester_form'))    
    person_distributed_by = CharFilter(
        label="Contratante",
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Person,
            field_related='legal_name',
            name='person_distributed_by',
            url='/service_form'))
    final_deadline_date_in = MDDateTimeRangeFilter(
        name='final_deadline_date_in', label='Prazo entre:')
    requested_in = MDDateTimeRangeFilter(
        name='requested_in', label=u"Solicitadas entre:")
    accepted_service_in = MDDateTimeRangeFilter(
        name='accepted_service_in', label="Aceitas pelo Service entre:")
    refused_service_in = MDDateTimeRangeFilter(
        name='refused_service_in', label="Recusadas pelo Service entre:")
    open_in = MDDateTimeRangeFilter(name='open_in', label="Abertas entre:")
    accepted_in = MDDateTimeRangeFilter(
        name='accepted_in', label="Aceitas entre:")
    refused_in = MDDateTimeRangeFilter(
        name='refused_in', label="Recusadas entre:")
    return_in = MDDateTimeRangeFilter(
        name='return_in', label="Retornadas entre:")
    done_in = MDDateTimeRangeFilter(name='done_in', label="Cumpridas entre:")
    blocked_payment_in = MDDateTimeRangeFilter(
        name='blocked_payment_in', label="Glosadas entre:")
    finished_in = MDDateTimeRangeFilter(
        name='finished_in', label="Finalizadas entre:")

    custom_filter = ModelChoiceFilter(
        queryset=filter_valid_choice_form(Filter.objects.all()),
        label="Escolher filtro salvo",
        required=False,
        widget=Select(attrs={'onchange': 'this.form.submit()'}))
    custom_filter_name = CharFilter(label=u"Nome do Filtro", required=False)

    custom_filter_description = CharFilter(
        label=u"Descrição",
        required=False,
        widget=Textarea(attrs={
            'class': 'form-control',
            'rows': '3'
        }))

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 request=None):
        super(TaskFilter, self).__init__(data, queryset, prefix, strict,
                                         request)
        self.filters['custom_filter'].queryset = Filter.objects.filter(
            create_user=self.request.user).order_by('name')
        filters_list = ['type_task', 'cost_center', 'court', 'team']
        office_session = get_office_session(self.request)
        for filter_field in filters_list:
            self.filters[filter_field].queryset = self.filters[
                filter_field].queryset.filter(office=office_session)
        custom_settings = getattr(office_session, 'customsettings', None)
        if custom_settings and custom_settings.task_status_show:
            task_status_choices = list(
                custom_settings.task_status_show.values_list(
                    'status_to_show', flat=True).order_by('status_to_show'))
            self.filters['task_status'].extra['choices'] = self.set_task_status_choices(task_status_choices)

    class Meta:
        model = DashboardViewModel
        fields = []
        order_by = ['final_deadline_date']

    @staticmethod
    def set_task_status_choices(status_choices):
        return list(map(lambda x: (TaskStatus(x).name, x), status_choices))


class BatchChangTaskFilter(TaskFilter):
    def __init__(self, data=None, queryset=None, prefix=None, strict=None, request=None):
        super().__init__(data, queryset, prefix, strict, request)
        status_to_filter = get_status_to_filter(request.option)
        self.filters['task_status'].extra['choices'] = self.set_task_status_choices(status_to_filter)


class TaskReportFilterBase(FilterSet):
    finished_in = MDDateTimeRangeFilter(name='finished_in')

    client = CharFilter(label="Cliente", required=False)
    office = CharFilter(label="Escritório Correspondente", required=False)

    class Meta:
        model = Task
        fields = []


class TaskToPayFilter(TaskReportFilterBase):
    status = ChoiceFilter(
        empty_label='Todas',
        choices=(
            (0, 'Somente faturadas'),
            (1, 'Somente não faturadas'),
        ))
    group_by_tasks = ChoiceFilter(
        empty_label=None,
        choices=GROUP_BY_TASK_TO_PAY_TYPE
    )
    refunds_correspondent_service = ChoiceFilter(
        label='Cliente reembolsa valor gasto com serviço de correspondência',
        empty_label='Todos',
        choices=(
            (True, 'Somente clientes que reembolsam'),
            (False, 'Somente clientes que não reembolsam'),
            )
        )


class TaskToReceiveFilter(TaskReportFilterBase):
    status = ChoiceFilter(
        empty_label='Todas',
        choices=(
            ('true', 'Somente recebidas'),
            ('false', 'Somente não recebidas'),
        ))
    group_by_tasks = ChoiceFilter(
        empty_label=None, choices=GROUP_BY_TASK_TO_RECEIVE_TYPE)
    parent_finished_in = MDDateTimeRangeFilter(name='parent_finished_in')


class TypeTaskMainFilter(filters.FilterSet):
    is_hearing = filters.BooleanFilter(name='is_hearing')
    name = filters.CharFilter(name='name', lookup_expr='unaccent__icontains')

    class Meta:
        model = TypeTaskMain
        fields = ['is_hearing', 'name']


class TaskCheckinReportFilter(FilterSet):
    finished_date = MDDateTimeRangeFilter(name='finished_date', label='TESTE')
    execution_date = MDDateTimeRangeFilter(name='execution_date')
    task_executed_by = CharFilter(name='executed_by_checkin__create_user__person__legal_name',
                                  lookup_expr='unaccent__icontains', label='Correspondente/Escritório contratado')
    task_company_representative = CharFilter(name='company_representative_checkin__create_user__person__legal_name',
                                             lookup_expr='unaccent__icontains', label='Preposto')
    has_checkin = ChoiceFilter(
        empty_label='Todas',
        label='Por check-in',
        method='has_checkin_filter',
        choices=(
            (0, 'Somente realizado'),
            (1, 'Somente não realizado'),
        ))

    class Meta:
        model = Task
        fields = ['finished_date', 'execution_date', 'task_executed_by', 'task_company_representative', 'has_checkin']

    def has_checkin_filter(self, queryset, name, value):
        if value == '0':
            return queryset.filter(Q(
                Q(executed_by_checkin__isnull=int(value)) |
                Q(company_representative_checkin__isnull=int(value))
            ))
        elif value == '1':
            return queryset.filter(Q(
                Q(executed_by_checkin__isnull=int(value)),
                Q(company_representative_checkin__isnull=int(value))
            ))
        return queryset
