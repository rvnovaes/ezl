from django.forms import Select, Textarea, RadioSelect
from django_filters import FilterSet, ModelChoiceFilter, NumberFilter, CharFilter, ChoiceFilter
from django import forms

from core.models import Person, State, Office
from core.utils import filter_valid_choice_form
from core.widgets import MDDateTimeRangeFilter, TypeaHeadForeignKeyWidget
from financial.models import CostCenter
from lawsuit.models import CourtDistrict, Organ
from task.models import TypeTask, Task, Filter
from .models import DashboardViewModel


class TaskFilter(FilterSet):
    state = ModelChoiceFilter(queryset=filter_valid_choice_form(
        State.objects.filter(is_active=True)),
        label="UF")
    court_district = CharFilter(label="Comarca",
                                required=False,
                                widget=TypeaHeadForeignKeyWidget(model=CourtDistrict,
                                                                 field_related='name',
                                                                 forward='state',
                                                                 name='court_district',
                                                                 url='/processos/courtdistrict_autocomplete'))

    type_task = ModelChoiceFilter(queryset=filter_valid_choice_form(TypeTask.objects.filter(is_active=True)),
                                  label=u"Tipo de Serviço")
    cost_center = ModelChoiceFilter(queryset=filter_valid_choice_form(CostCenter.objects.filter(is_active=True)),
                                    label="Setor")
    court = ModelChoiceFilter(queryset=filter_valid_choice_form(Organ.objects.filter(is_active=True)),
                              label="Órgão")
    folder_number = NumberFilter(label=u"Nº da pasta")
    folder_legacy_code = CharFilter(label=u"Nº da pasta de origem")
    law_suit_number = CharFilter(label=u"Nº do processo")
    task_number = NumberFilter(label=u"Nº da OS")
    task_legacy_code = CharFilter(label=u"Nº da OS de origem")
    client = CharFilter(label="Cliente",
                        required=False,
                        widget=TypeaHeadForeignKeyWidget(model=Person,
                                                         field_related='legal_name',
                                                         name='client',
                                                         url='/client_form'))
    person_executed_by = CharFilter(label="Correspondente",
                        required=False,
                        widget=TypeaHeadForeignKeyWidget(model=Person,
                                                         field_related='legal_name',
                                                         name='person_executed_by',
                                                         url='/correspondent_form'))
    person_asked_by = CharFilter(label="Solicitante",
                                    required=False,
                                    widget=TypeaHeadForeignKeyWidget(model=Person,
                                                                     field_related='legal_name',
                                                                     name='person_asked_by',
                                                                     url='/requester_form'))
    person_distributed_by = CharFilter(label="Contratante",
                                 required=False,
                                 widget=TypeaHeadForeignKeyWidget(model=Person,
                                                                  field_related='legal_name',
                                                                  name='person_distributed_by',
                                                                  url='/service_form'))
    requested_in = MDDateTimeRangeFilter(name='requested_in', label=u"Solicitadas entre:")
    accepted_service_in = MDDateTimeRangeFilter(name='accepted_service_in', label="Aceitas pelo Service entre:")
    refused_service_in = MDDateTimeRangeFilter(name='refused_service_in', label="Recusadas pelo Service entre:")
    open_in = MDDateTimeRangeFilter(name='open_in', label="Abertas entre:")
    accepted_in = MDDateTimeRangeFilter(name='accepted_in', label="Aceitas entre:")
    refused_in = MDDateTimeRangeFilter(name='refused_in', label="Recusadas entre:")
    return_in = MDDateTimeRangeFilter(name='return_in', label="Retornadas entre:")
    done_in = MDDateTimeRangeFilter(name='done_in', label="Cumpridas entre:")
    blocked_payment_in = MDDateTimeRangeFilter(name='blocked_payment_in', label="Glosadas entre:")
    finished_in = MDDateTimeRangeFilter(name='finished_in', label="Finalizadas entre:")

    custom_filter = ModelChoiceFilter(queryset=filter_valid_choice_form(Filter.objects.all()),
                                      label="Escolher filtro salvo",
                                      required=False,
                                      widget=Select(attrs={'onchange': 'this.form.submit()'}))
    custom_filter_name = CharFilter(label=u"Nome do Filtro", required=False)

    custom_filter_description = CharFilter(label=u"Descrição", required=False,
                                           widget=Textarea(attrs={'class': 'form-control',
                                                                  'rows': '3'}))

    def __init__(self, data=None, queryset=None, prefix=None, strict=None, request=None):
        super(TaskFilter, self).__init__(data, queryset, prefix, strict, request)
        self.filters['custom_filter'].queryset = Filter.objects.filter(create_user=self.request.user).order_by('name')

    class Meta:
        model = DashboardViewModel
        fields = []
        order_by = ['final_deadline_date']


class TaskToPayFilter(FilterSet):

    finished_in = MDDateTimeRangeFilter(name='finished_in')

    billed = ChoiceFilter(
        empty_label='Todas',
        choices=(
            ('true', 'Somente faturadas'),
            ('false', 'Somente não faturadas'),
            )
        )

    client = CharFilter(label="Cliente",
                        required=False,
                        widget=TypeaHeadForeignKeyWidget(model=Person,
                                                         field_related='legal_name',
                                                         name='client',
                                                         url='/client_form'))
    office = CharFilter(label="Escritório Correspondente",
                        required=False,
                        widget=TypeaHeadForeignKeyWidget(model=Office,
                                                         field_related='name',
                                                         name='office',
                                                         url='/office_form'))

    class Meta:
        model = Task
        fields = []

