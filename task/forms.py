from datetime import datetime

import pytz
from django import forms
from django.forms import fields_for_model, ModelForm

from core.models import Person
from ezl import settings
from lawsuit.forms import BaseForm
from lawsuit.models import Movement, TypeMovement
from task.models import Task


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

    first_deadline_date = forms.DateTimeField(required=False
                                              )

    second_deadline_date = forms.DateTimeField(required=False
                                               )

    execution_date = forms.DateTimeField(required=False
                                         )

    return_date = forms.DateTimeField(required=False
                                      )
    refused_date = forms.DateTimeField(required=False
                                       )


class TaskDetailForm(ModelForm):
    class Meta:
        model = Task
        fields = fields_for_model(Task,
                                  exclude={'legacy_code', 'movement', 'person_asked_by', "person_executed_by",
                                           'type_movement',
                                           'delegation_date', 'acceptance_date', "reminder_deadline_date",
                                           "final_deadline_date",
                                           # 'execution_date',
                                           'return_date', 'refused_date', 'create_user', 'alter_date',
                                           'create_date', 'alter_user', 'is_active', 'notes'})

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
    # reminder_deadline_date = forms.DateTimeField(required=False
    #                                              )
    #
    # final_deadline_date = forms.DateTimeField(required=False
    #                                           )
    #
    execution_date = forms.DateTimeField(required=False,
                                         initial=datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                         label=u"Data de Cumprimento",
                                         widget=forms.DateTimeInput(
                                             attrs={'class': 'form-control', 'type': 'datetime-local'},
                                             format='%Y-%m-%d %H:%M:%S')

                                         )
    #
    # return_date = forms.DateTimeField(required=False
    #                                   )
    # refused_date = forms.DateTimeField(required=False
    #                                    )

    # def __init__(self, *args, **kwargs):
    #     super(BaseForm, self).__init__(*args, **kwargs)
    #
    #     for field_name, field in self.fields.items():
    #         field.widget.attrs['disabled'] = 'true'
    #         if field.widget.input_type != 'checkbox':
    #             field.widget.attrs['class'] = 'form-control'
    #         if field.widget.input_type == 'text':
    #             field.widget.attrs['style'] = 'width: 100%; display: table-cell; '
    #         try:
    #             field.label = self._meta.model._meta.get_field(field_name).verbose_name
    #         except FieldDoesNotExist:
    #             pass
    #             # fields = fields_for_model(Task,
    #             #                           exclude={'create_user', 'alter_date', 'create_date', 'alter_user','is_active'})
