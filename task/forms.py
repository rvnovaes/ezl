from datetime import datetime

import pytz
from django import forms
from django.forms import ModelForm

from core.models import Person
from core.widgets import MDDateTimepicker
from ezl import settings
from lawsuit.forms import BaseForm
from lawsuit.models import Movement, TypeMovement
from task.models import Task, Ecm


class TaskForm(BaseForm):
    class Meta:
        model = Task
        fields = ['legacy_code', 'movement', 'person_asked_by', "person_executed_by", 'type_movement',
                  'delegation_date', 'acceptance_date', "reminder_deadline_date", "final_deadline_date",
                  'execution_date',
                  'return_date', 'refused_date']

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
        required=True
    )

    movement = forms.ModelChoiceField(
        queryset=Movement.objects.filter(is_active=True),
        empty_label=u"Selecione...",
        label=u"Movimentação"
    )

    person_asked_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(is_active=True, is_correspondent=False)

    )

    person_executed_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(is_active=True, is_correspondent=True)

    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(is_active=True),
        empty_label=u"Selecione...",
        label=u"Tipo de Movimentação"
    )
    # TODO verificar como aplicar os formulários com dateTimeField

    delegation_date = forms.DateTimeField(
    )

    acceptance_date = forms.DateTimeField(required=False
                                          )

    reminder_deadline_date = forms.DateTimeField(required=False
                                                 )

    final_deadline_date = forms.DateTimeField(required=False
                                              )

    execution_date = forms.DateTimeField(required=False
                                         )

    return_date = forms.DateTimeField(required=False
                                      )
    refused_date = forms.DateTimeField(required=False
                                       )


class TaskDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['execution_date'].widget.min_date = self.instance.acceptance_date

    class Meta:
        model = Task
        # fields = ['legacy_code', 'movement', 'person_asked_by', "person_executed_by",
        #           'type_movement',
        #           'delegation_date', 'acceptance_date', "reminder_deadline_date",
        #           "final_deadline_date",
        fields = ['execution_date']
        # 'return_date', 'refused_date', \
        # 'create_user', 'alter_date',
        # 'alter_user', 'is_active']

    # legacy_code = forms.CharField(
    #     label=u"Código Legado",
    #     max_length=255,
    #     required=False
    # )
    #
    # movement = forms.ModelChoiceField(
    #     queryset=Movement.objects.filter(is_active=True),
    #     empty_label=u"Selecione...",
    #     label=u"Movimentação",
    #     required=False
    # )
    #
    # person_asked_by = forms.ModelChoiceField(
    #     empty_label=u"Selecione...",
    #     queryset=Person.objects.filter(is_active=True, is_correspondent=False),
    #     required=False
    #
    # )
    #
    # person_executed_by = forms.ModelChoiceField(
    #     empty_label=u"Selecione...",
    #     queryset=Person.objects.filter(is_active=True, is_correspondent=True),
    #     required=False
    #
    # )
    #
    # type_movement = forms.ModelChoiceField(
    #     queryset=TypeMovement.objects.filter(is_active=True),
    #     empty_label=u"Selecione...",
    #     label=u"Tipo de Movimentação",
    #     required=False
    # )
    # # TODO verificar como aplicar os formulários com dateTimeField
    # delegation_date = forms.DateTimeField(required=False
    #                                       )
    #
    # acceptance_date = forms.DateTimeField(required=False
    #                                       )
    #
    # create_date = forms.DateTimeField(required=False
    #                                              )
    #
    # final_deadline_date = forms.DateTimeField(required=False
    #                                           )
    #
    execution_date = forms.DateTimeField(required=False,
                                         initial=datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                         label=u"Data de Cumprimento",
                                         widget=MDDateTimepicker(attrs={'class': 'form-control'}
                                                                 # min_date="12-06-2017"
                                                                 # attrs={'class': 'form-control', 'type': 'text'}
                                                                 # format='%Y-%m-%d %H:%M:%S')
                                                                 ))
    notes = forms.CharField(
        required=True,
        initial="",
        label=u"Insira um comentário",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'type': 'text', 'cols': '5', 'id': 'textarea1'}
        )
    )


    # return_date = forms.DateTimeField(required=False
    #                                   )
    # refused_date = forms.DateTimeField(required=False
    #                                    )

    # def __init__(self, *args, **kwargs):
    #     super(TaskDetailForm, self).__init__(*args, **kwargs)
    #
    #     self.cleaned_data['reminder_deadline_date'] = self.instance.reminder_deadline_date
    #     # for field_name, field in self.fields.items():
    #     field.widget.attrs['disabled'] = 'true'
    #     if field.widget.input_type != 'checkbox':
    #         field.widget.attrs['class'] = 'form-control'
    #     if field.widget.input_type == 'text':
    #         field.widget.attrs['style'] = 'width: 100%; display: table-cell; '
    #     try:
    #             field.label = self._meta.model._meta.get_field(field_name).verbose_name
    #         except FieldDoesNotExist:
    #             pass
    #             # fields = fields_for_model(Task,
    #             #                           exclude={'create_user', 'alter_date', 'create_date', 'alter_user','is_active'})


class EcmForm(BaseForm):
    class Meta:
        model = Ecm
        fields = ['path', 'task']

    path = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
