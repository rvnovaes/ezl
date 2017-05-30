from django import forms

from core.models import Person
from lawsuit.forms import BaseForm
from lawsuit.models import Movement, TypeMovement
from task.models import Task


class TaskForm(BaseForm):
    class Meta:
        model = Task
        fields = ['legacy_code', 'movement', 'person_asked_by', "person_executed_by", 'type_movement',
                  'delegation_date', 'acceptance_date', 'first_deadline_date', 'second_deadline_date', 'execution_date',
                  'return_date', 'refused_date']

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
        required=True
    )

    movement = forms.ModelChoiceField(
        queryset=Movement.objects.filter(active=True),
        empty_label=u"Selecione...",
        label=u"Movimentação"
    )

    person_asked_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(active=True, is_corresponding=False)

    )

    person_executed_by = forms.ModelChoiceField(
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(active=True, is_corresponding=True)

    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(active=True),
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
