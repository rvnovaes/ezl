from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from django_file_form.forms import FileFormMixin, MultipleUploadedFileField

from core.models import Person
from core.utils import filter_valid_choice_form, get_office_field
from core.widgets import MDDateTimepicker, MDDatePicker
from lawsuit.forms import BaseForm
from task.models import Task, TypeTask, Filter


class TaskForm(BaseForm):
    task_number = forms.CharField(disabled=True, required=False,
                                  widget=forms.TextInput(attrs={
                                      'placeholder': 'Gerado automaticamente'}))

    class Meta:
        model = Task
        fields = ['office',
                  'task_number', 'type_task',
                  'person_executed_by', 'person_asked_by', 'person_distributed_by',
                  'final_deadline_date',
                  'delegation_date', 'acceptance_date', 'refused_date', 'execution_date',
                  'return_date', 'blocked_payment_date', 'finished_date', 'description',
                  'is_active']

    person_asked_by = forms.ModelChoiceField(
        empty_label='Selecione...',
        queryset=filter_valid_choice_form(
            Person.objects.active().requesters().order_by('name')))

    person_executed_by = forms.ModelChoiceField(
        empty_label='Selecione...',
        queryset=Person.objects.active().correspondents().order_by('name'))

    person_distributed_by = forms.ModelChoiceField(
        empty_label='Selecione...',
        queryset=Person.objects.active().services().order_by('name'),
        label='Contratante')

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(
            TypeTask.objects.filter(is_active=True)).order_by('name'),
        empty_label='Selecione...',
        label='Tipo de Serviço')

    delegation_date = forms.DateTimeField(initial=datetime.now(),
                                          required=True,
                                          label='Data de Delegação',
                                          widget=MDDateTimepicker(attrs={
                                              'class': 'form-control'
                                          },
                                              format='DD/MM/YYYY'))

    acceptance_date = forms.DateTimeField(required=False,
                                          widget=MDDateTimepicker(attrs={
                                              'class': 'form-control'
                                          },
                                              format='DD/MM/YYYY'))

    final_deadline_date = forms.DateTimeField(required=True,
                                              widget=MDDateTimepicker(attrs={
                                                  'class': 'form-control'
                                              },
                                                  format='DD/MM/YYYY HH:mm'))

    execution_date = forms.DateTimeField(required=False,
                                         widget=MDDateTimepicker(attrs={
                                             'class': 'form-control'
                                         },
                                             format='DD/MM/YYYY'))

    return_date = forms.DateTimeField(required=False,
                                      widget=MDDateTimepicker(attrs={
                                          'class': 'form-control'
                                      },
                                          format='DD/MM/YYYY'))

    refused_date = forms.DateTimeField(required=False,
                                       widget=MDDateTimepicker(attrs={
                                           'class': 'form-control'
                                       },
                                           format='DD/MM/YYYY'))

    blocked_payment_date = forms.DateTimeField(required=False,
                                               widget=MDDateTimepicker(attrs={
                                                   'class': 'form-control'
                                               },format='DD/MM/YYYY'))

    finished_date = forms.DateTimeField(required=False,
                                        widget=MDDateTimepicker(attrs={
                                            'class': 'form-control'
                                        },
                                            format='DD/MM/YYYY'))

    description = forms.CharField(required=False, initial='', label='Descrição',
                                  widget=forms.Textarea(
                                      attrs={'class': 'form-control', 'rows': '5',
                                             'id': 'details_id'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class TaskCreateForm(FileFormMixin, TaskForm):
    documents = forms.FileField(widget=forms.ClearableFileInput(
                                attrs={'multiple': True,
                                       "id": "fileupload-create"}),
                                required=False)


    class Meta(TaskForm.Meta):
        fields = TaskForm.Meta.fields + ['documents']


class TaskDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['execution_date'].widget.max_date = timezone.now()

    class Meta:
        model = Task
        fields = ['execution_date', 'survey_result']

    survey_result = forms.CharField(required=False, initial=None)

    execution_date = forms.DateTimeField(required=False,
                                         initial=timezone.now(),
                                         label='Data de Cumprimento',
                                         widget=MDDateTimepicker(attrs={
                                             'class': 'form-control',
                                         },
                                             format='DD/MM/YYYY HH:mm'))
    notes = forms.CharField(
        required=False,
        initial='',
        label='Insira um comentário',
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'cols': '5', 'id': 'notes_id'}
        )
    )

    amount = forms.CharField(
        required=False,
        label='Valor:',
        widget=forms.TextInput(attrs={'mask': 'money'})
    )

    servicepricetable_id = forms.CharField(required=False,
                                           widget=forms.HiddenInput())

    def clean_servicepricetable_id(self):
        servicepricetable_id = self.cleaned_data['servicepricetable_id']
        amount = (self.cleaned_data['amount'] if self.cleaned_data['amount'] else 0)
        if amount and amount >= 0.0 and not servicepricetable_id:
            raise forms.ValidationError("Favor Selecionar um correspondente")
        return servicepricetable_id

    def clean_amount(self):
        amount = (self.cleaned_data['amount'] if self.cleaned_data['amount'] else str(0))
        amount = amount.replace('.', '')
        amount = amount.replace(',', '.')
        return float(amount)

    def clean(self):
        form_data = self.cleaned_data
        return form_data


class TypeTaskForm(BaseForm):
    class Meta:
        model = TypeTask
        fields = ['office', 'name', 'survey', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class FilterForm(BaseForm):
    name = forms.CharField(label=u"Nome", required=True,
                                  widget=forms.Textarea(
                                      attrs={'rows': '1'}))
    description = forms.CharField(label=u"Descrição", required=False,
                                           widget=forms.Textarea(
                                               attrs={'rows': '3'}))
    class Meta:
        model = Filter
        fields = ['name', 'description']

class TaskToAssignForm(BaseForm):
    class Meta:
        model = Task
        fields = ['person_executed_by']
