from datetime import datetime, timedelta

import pytz
from django import forms
from django.forms import ModelForm

from core.models import Person
from core.widgets import MDDateTimepicker, MDDatePicker
from ezl import settings
from lawsuit.forms import BaseForm
from .models import Task, Ecm, TypeTask
from core.utils import filter_valid_choice_form


class TaskForm(BaseForm):
    class Meta:
        model = Task
        fields = ['type_task', "person_executed_by", 'person_asked_by', "reminder_deadline_date",
                  "final_deadline_date", 'delegation_date', 'acceptance_date', 'refused_date', 'execution_date',
                  'return_date', 'blocked_payment_date', 'finished_date', 'is_active']

    person_asked_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=filter_valid_choice_form(Person.objects.filter(is_active=True, is_correspondent=False)).order_by('name')

    )

    person_executed_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(is_active=True, is_correspondent=True).order_by('name')

    )

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeTask.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione...",
        label=u"Tipo de Serviço"
    )
    # TODO verificar como aplicar os formulários com dateTimeField

    delegation_date = forms.DateTimeField(show_hidden_initial=True, initial=datetime.now(),
                                          required=True,
                                          widget=MDDatePicker(attrs={'class': 'form-control'},
                                                              format='DD/MM/YYYY'
                                                              )
                                          )

    acceptance_date = forms.DateTimeField(required=False,
                                          widget=MDDatePicker(attrs={'class': 'form-control'},
                                                              format='DD/MM/YYYY'
                                                              )
                                          )

    reminder_deadline_date = forms.DateField(required=True,
                                             widget=MDDatePicker(attrs={'class': 'form-control'},
                                                                 format='DD/MM/YYYY')
                                             )

    final_deadline_date = forms.DateTimeField(required=False,
                                              widget=MDDatePicker(attrs={'class': 'form-control'},
                                                                  format='DD/MM/YYYY')
                                              )

    execution_date = forms.DateTimeField(required=False,
                                         widget=MDDatePicker(attrs={'class': 'form-control'},
                                                             format='DD/MM/YYYY')
                                         )

    return_date = forms.DateTimeField(required=False,
                                      widget=MDDatePicker(attrs={'class': 'form-control'},
                                                          format='DD/MM/YYYY')
                                      )
    refused_date = forms.DateTimeField(required=False,
                                       widget=MDDatePicker(attrs={'class': 'form-control'},
                                                           format='DD/MM/YYYY')
                                       )

    blocked_payment_date = forms.DateTimeField(required=False,
                                               widget=MDDatePicker(attrs={'class': 'form-control'},
                                                                   format='DD/MM/YYYY')
                                               )

    finished_date = forms.DateTimeField(required=False,
                                        widget=MDDatePicker(attrs={'class': 'form-control'},
                                                            format='DD/MM/YYYY')
                                        )


class TaskDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['execution_date'].widget.min_date = self.instance.acceptance_date

    class Meta:
        model = Task
        fields = ['execution_date', 'survey_result']

    survey_result = forms.CharField(required=False, initial=None)

    execution_date = forms.DateTimeField(required=False,
                                         initial=datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                         label=u"Data de Cumprimento",
                                         widget=MDDateTimepicker(attrs={'class': 'form-control'},
                                                                 format='DD/MM/YYYY HH:mm',
                                                                 ))
    notes = forms.CharField(
        required=True,
        initial="",
        label=u"Insira um comentário",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'cols': '5', 'id': 'notes_id'}
        )
    )


class EcmForm(BaseForm):
    class Meta:
        model = Ecm
        fields = ['path', 'task']

    path = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class TypeTaskForm(BaseForm):
    class Meta:
        model = TypeTask
        fields = ['name', 'survey_type', 'is_active']
