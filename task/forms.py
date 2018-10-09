import json
from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django_file_form.forms import MultipleUploadedFileField

from core.models import Person, ImportXlsFile
from core.utils import filter_valid_choice_form, get_office_field, get_office_session
from core.widgets import MDDateTimepicker, MDDatePicker
from core.forms import BaseForm, XlsxFileField
from task.models import Task, TypeTask, Filter, TaskStatus, TypeTaskMain
from task.resources import COLUMN_NAME_DICT
from task.widgets import code_mirror_schema
from .schemas import *
from .fields import JSONFieldMixin
from survey.models import Survey


class TaskForm(BaseForm):
    task_number = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Gerado automaticamente'}))

    class Meta:
        model = Task
        fields = [
            'office', 'task_number', 'person_asked_by', 'type_task',
            'final_deadline_date', 'performance_place', 'description', 'is_active'
        ]

    person_asked_by = forms.ModelChoiceField(
        empty_label='Selecione...',
        queryset=filter_valid_choice_form(Person.objects.active().requesters().
                                          active_offices().order_by('name')))

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(
            TypeTask.objects.filter(is_active=True)).order_by('name'),
        empty_label='Selecione...',
        label='Tipo de Serviço')

    final_deadline_date = forms.DateTimeField(
        required=True,
        label="Prazo Fatal",
        widget=MDDateTimepicker(
            attrs={'class': 'form-control'}, format='DD/MM/YYYY HH:mm'))

    description = forms.CharField(
        required=False,
        initial='',
        label='Descrição',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '5',
            'id': 'details_id'
        }))

    performance_place = forms.CharField(required=True)
    documents = MultipleUploadedFileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        office_session = get_office_session(self.request)
        if office_session:
            self.fields['person_asked_by'].queryset = filter_valid_choice_form(
                Person.objects.active().requesters(
                    office_id=office_session.pk).active_offices().order_by(
                        'name'))
            self.fields['type_task'].queryset = filter_valid_choice_form(
                TypeTask.objects.filter(
                    is_active=True, office=office_session)).order_by('name')
        else:
            self.fields['type_task'].queryset = TypeTask.objects.none()
        if self.request.user:
            if Person.objects.requesters().filter(auth_user=self.request.user):
                self.fields[
                    'person_asked_by'].initial = self.request.user.person


class TaskCreateForm(TaskForm):
    documents = MultipleUploadedFileField(required=False)

    class Meta(TaskForm.Meta):
        fields = TaskForm.Meta.fields + ['documents']


class TaskDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['execution_date'].widget.max_date = timezone.now()

    class Meta:
        model = Task
        fields = ['execution_date', 'survey_result']

    survey_result = forms.CharField(
        required=False, initial=None, widget=forms.HiddenInput())

    execution_date = forms.DateTimeField(
        required=False,
        initial=timezone.now(),
        label='Data de Cumprimento',
        widget=MDDateTimepicker(
            attrs={
                'class': 'form-control',
            }, format='DD/MM/YYYY HH:mm'))
    notes = forms.CharField(
        required=False,
        initial='',
        label='Insira um comentário',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'cols': '5',
            'id': 'notes_id'
        }))

    amount = forms.CharField(
        required=False,
        label='Valor:',
        widget=forms.TextInput(attrs={'mask': 'money'}))

    servicepricetable_id = forms.CharField(
        required=False, widget=forms.HiddenInput())

    feedback_rating = forms.IntegerField(label="Nota", required=False)
    feedback_comment = forms.CharField(
        label="Comentário sobre o atendimento do correspondente",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}))

    def clean_amount(self):
        amount = (self.cleaned_data['amount']
                  if self.cleaned_data['amount'] else str(0))
        amount = amount.replace('.', '')
        amount = amount.replace(',', '.')
        return float(amount)

    def clean(self):
        form_data = self.cleaned_data
        return form_data


class FilterForm(BaseForm):
    name = forms.CharField(
        label=u"Nome",
        required=True,
        widget=forms.Textarea(attrs={'rows': '1'}))
    description = forms.CharField(
        label=u"Descrição",
        required=False,
        widget=forms.Textarea(attrs={'rows': '3'}))

    class Meta:
        model = Filter
        fields = ['name', 'description']


class TaskToAssignForm(BaseForm):
    class Meta:
        model = Task
        fields = ['person_executed_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person_executed_by'].required = True


class TypeTaskMainForm(forms.ModelForm):
    characteristics = JSONFieldMixin(
        label="Caractersíticas",
        widget=code_mirror_schema,
        initial=CHARACTERISTICS)

    class Meta:
        model = TypeTaskMain
        fields = '__all__'


class TypeTaskForm(BaseForm):
    class Meta:
        model = TypeTask
        fields = ['office', 'type_task_main', 'survey', 'name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        office = get_office_session(self.request)
        self.fields['office'] = get_office_field(self.request)
        self.fields['survey'].queryset = Survey.objects.filter(office=office)
        self.order_fields(
            ['office', 'type_task_main', 'survey', 'name', 'is_active'])


class ImportTaskListForm(forms.ModelForm):
    file_xls = XlsxFileField(
        label='Arquivo', required=True, headers_to_check=[])

    class Meta:
        model = ImportXlsFile
        fields = ('file_xls', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_xls'].headers_to_check.extend([
            v['column_name'] for k, v in COLUMN_NAME_DICT.items()
            if v['required']
        ])
