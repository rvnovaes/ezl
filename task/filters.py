from django.forms import Select, Textarea
from django_filters import FilterSet, ModelChoiceFilter, NumberFilter, CharFilter
from django import forms

from core.models import Person, State
from core.utils import filter_valid_choice_form
from core.widgets import MDDateTimeRangeFilter, MDModelSelect2
from financial.models import CostCenter
from lawsuit.models import CourtDistrict, Organ
from task.models import TypeTask, Filter
from .models import DashboardViewModel


class TaskFilter(FilterSet):
    state = ModelChoiceFilter(queryset=filter_valid_choice_form(
        State.objects.filter(is_active=True).order_by('name')),
                              label="UF")
    court_district = ModelChoiceFilter(queryset=CourtDistrict.objects.filter(),
                                       name="court_district",
                                       widget=MDModelSelect2(
                                           url='courtdistrict_autocomplete',
                                           forward=['state'],
                                           attrs={
                                               'class': '',
                                               'data-placeholder': '',
                                               'data-label': 'Comarca'
                                           }),
                                       required=False,
                                       label="Comarca")
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

    client = ModelChoiceFilter(queryset=Person.objects.filter(),
                               label="Cliente",
                               name='client',
                               required=False,
                               widget=MDModelSelect2(url='client_autocomplete',
                                                     attrs={
                                                         'class': 'select-with-search material-ignore form-control',
                                                         'data-placeholder': '',
                                                         'data-label': 'Cliente'
                                                     })
                               )

    person_executed_by = ModelChoiceFilter(queryset=Person.objects.filter(),
                                           label="Correspondente",
                                           name='person_executed_by',
                                           required=False,
                                           widget=MDModelSelect2(url='correspondent_autocomplete',
                                                                 attrs={
                                                                        'class': '',
                                                                        'data-placeholder': '',
                                                                        'data-label': 'Correspondente'
                                                                       })
                                           )

    person_asked_by = ModelChoiceFilter(queryset=Person.objects.filter(),
                                        label="Solicitante",
                                        name='person_asked_by',
                                        required=False,
                                        widget=MDModelSelect2(url='requester_autocomplete',
                                                              attrs={
                                                                 'class': '',
                                                                 'data-placeholder': '',
                                                                 'data-label': 'Solicitante'
                                                                    })
                                        )

    person_distributed_by = ModelChoiceFilter(queryset=Person.objects.filter(),
                                              label="Contratante",
                                              name='person_distributed_by',
                                              required=False,
                                              widget=MDModelSelect2(url='service_autocomplete',
                                                                    attrs={
                                                                        'class': '',
                                                                        'data-placeholder': '',
                                                                        'data-label': 'Contratante'
                                                                    })
                                              )

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
                                      label=" / Escolher filtro salvo",
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
