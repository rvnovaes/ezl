from django_filters import FilterSet, BooleanFilter, ModelChoiceFilter

from core.models import Person
from core.widgets import MDCheckboxInput, MDDateTimeRangeFilter, MDModelSelect2
from .models import Task, DashboardViewModel


class TaskFilter(FilterSet):
    openned = BooleanFilter(required=False, widget=MDCheckboxInput, label="Em aberto", name='openned')
    accepted = BooleanFilter(required=False, widget=MDCheckboxInput, label="Aceitas", name='accepted')
    refused = BooleanFilter(required=False, widget=MDCheckboxInput, label="Recusadas", name='refused')
    done = BooleanFilter(required=False, widget=MDCheckboxInput, label="Cumpridas", name='done')
    returned = BooleanFilter(required=False, widget=MDCheckboxInput, label="Retornadas", name='returned')
    blocked = BooleanFilter(required=False, widget=MDCheckboxInput, label="Glosadas", name='blocked_payment')
    finished = BooleanFilter(required=False, widget=MDCheckboxInput, label="Finalizadas", name='finished')

    reminder = MDDateTimeRangeFilter(name="Prazo Inicial", label="Prazo Inicial",
                                     )
    deadline = MDDateTimeRangeFilter(label="Prazo Final", name="Prazo Final", format="DD/MM/YYYY HH:mm"
                                     )

    client = ModelChoiceFilter(queryset=Person.objects.all(),
                               lookup_expr='cli', label="Cliente",
                               name='client',
                               widget=MDModelSelect2(url='client_autocomplete', attrs={'class': 'form-control'}))

    class Meta:
        model = DashboardViewModel
        fields = []
        order_by = ['final_deadline_date']
