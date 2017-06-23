from datetime import datetime

from django import forms
from django_filters import FilterSet, BooleanFilter, CharFilter

from core.widgets import MDCheckboxInput, MDDateTimeRangeFilter
from .models import Task


class TaskFilter(FilterSet):
    year = datetime.now().year

    openned = BooleanFilter(required=False, widget=MDCheckboxInput, label="Em aberto", name='openned')
    accepted = BooleanFilter(required=False, widget=MDCheckboxInput, label="Aceitas", name='accepted')
    refused = BooleanFilter(required=False, widget=MDCheckboxInput, label="Recusadas", name='refused')
    done = BooleanFilter(required=False, widget=MDCheckboxInput, label="Cumpridas", name='done')
    returned = BooleanFilter(required=False, widget=MDCheckboxInput, label="Retornadas", name='returned')

    reminder = MDDateTimeRangeFilter(name="Prazo Inicial", label="Prazo Inicial",
                                     )
    deadline = MDDateTimeRangeFilter(label="Prazo Final", name="Prazo Final",
                                     )

    client = CharFilter(lookup_expr='cli', label="Cliente", name='client', widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))

    class Meta:
        model = Task
        # fields = ['legacy_code', 'movement', 'person_asked_by', 'person_executed_by',
        #          'delegation_date', 'reminder_deadline_date','final_deadline_date' ]
        fields = []
        order_by = ['final_deadline_date']
