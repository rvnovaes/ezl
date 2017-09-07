from datetime import datetime

import pytz
from django import forms
from django.forms import ModelForm
from django.forms.models import fields_for_model

from core.models import Person
from core.widgets import MDDateTimepicker, MDDatePicker
from ezl import settings
from lawsuit.forms import BaseForm
from .models import Task, Ecm, TypeTask


class TaskForm(BaseForm):
    class Meta:
        model = Task
        fields = ['type_task', "person_executed_by", 'person_asked_by', "reminder_deadline_date",
                  "final_deadline_date", 'delegation_date', 'acceptance_date', 'refused_date', 'execution_date',
                  'return_date', 'blocked_payment_date', 'finished_date', 'is_active']

    #
    # legacy_code = forms.CharField(
    #     label=u"Código Legado",
    #     max_length=255,
    #     required=False
    # )

    # movement = forms.ModelChoiceField(
    #     queryset=Movement.objects.filter(is_active=True),
    #     empty_label=u"Selecione...",
    #     label=u"Movimentação"
    # )

    person_asked_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(is_active=True, is_correspondent=False).order_by('name')

    )

    person_executed_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(is_active=True, is_correspondent=True).order_by('name')

    )

    type_task = forms.ModelChoiceField(
        queryset=TypeTask.objects.filter(is_active=True).order_by('name'),
        empty_label=u"Selecione...",
        label=u"Tipo de Serviço"
    )
    # TODO verificar como aplicar os formulários com dateTimeField

    delegation_date = forms.DateTimeField(

        widget=MDDatePicker(attrs={'class': 'form-control'},
                            format='DD/MM/YYYY'
                            )
    )

    acceptance_date = forms.DateTimeField(required=False,
                                          widget=MDDatePicker(attrs={'class': 'form-control'},
                                                              format='DD/MM/YYYY'
                                                              )
                                          )

    reminder_deadline_date = forms.DateTimeField(required=False,
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
        # self.fields['status'] = self.instance.status

    # def deliver_notes(self, notes):
    #     send_notes_execution_date.send(sender=self.__class__, notes=notes)

    class Meta:
        model = Task
        fields = ['execution_date', 'survey_result']

    survey_result = forms.CharField(required=False, initial=None)

    execution_date = forms.DateTimeField(required=False,
                                         initial=datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                         label=u"Data de Cumprimento",
                                         widget=MDDateTimepicker(attrs={'class': 'form-control'},
                                                                 format='DD/MM/YYYY HH:mm'
                                                                 ))
    notes = forms.CharField(
        required=True,
        initial="",
        label=u"Insira um comentário",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'type': 'text', 'cols': '5', 'id': 'textarea1'}
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
        fields = fields_for_model(TypeTask,
                                  exclude=['create_user', 'alter_date', 'create_date', 'alter_user',
                                           'legacy_code', 'system_prefix'])
        fields = ['name', 'survey_type', 'is_active']
