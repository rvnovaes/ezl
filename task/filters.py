from datetime import datetime

import django_filters as df
from django.forms.extras import SelectDateWidget

from core.widgets import MDCheckboxInput
from .models import Task


class TaskFilter(df.FilterSet):
    year = datetime.now().year

    openned = df.ChoiceFilter(widget=MDCheckboxInput, label="Em aberto", name='openned')
    accepted = df.ChoiceFilter(widget=MDCheckboxInput, label="Aceitas", name='accepted')
    refused = df.ChoiceFilter(widget=MDCheckboxInput, label="Recusadas", name='refused')
    done = df.ChoiceFilter(widget=MDCheckboxInput, label="Cumpridas", name='done')
    returned = df.ChoiceFilter(widget=MDCheckboxInput, label="Retornadas", name='returned')

    reminder_init = df.DateFilter(widget=SelectDateWidget(years=range(2008, year + 1)), name='Lembrete',
                                  lookup_expr='rem', label="Lembrete")
    reminder_end = df.DateFilter(widget=SelectDateWidget(years=range(2008, year + 1)), name='Lembrete',
                                 lookup_expr='rem', label="a")
    deadline_init = df.DateFilter(widget=SelectDateWidget(years=range(2008, year + 1)), name='PrazoFinal',
                                  lookup_expr='dl', label="Prazo Final")
    deadline_end = df.DateFilter(widget=SelectDateWidget(years=range(2008, year + 1)), name='PrazoFinal',
                                 lookup_expr='dl', label="a")

    cliente = df.CharFilter(lookup_expr='cli', label="Cliente", name='cliente')

    class Meta:
        model = Task
        # fields = ['legacy_code', 'movement', 'person_asked_by', 'person_executed_by',
        #          'delegation_date', 'reminder_deadline_date','final_deadline_date' ]
        fields = []
        order_by = ['final_deadline_date']
