import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from core.tables import CheckBoxMaterial
from task.models import Task


class IconColumn(tables.Column):
    def render(self, value):
        return format_html(
            '<i class="material-icons" data-toggle="tooltip" data-placement="bottom" title={} data-original-title="Tooltip on bottom">done</i>',
            value)


class TaskTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    legacy_code = tables.LinkColumn(viewname='task_update', attrs={'a': {'target': 'task_update'}}, args=[A('pk')])
    status = IconColumn('status')

    class Meta:
        model = Task
        fields = ['selection', 'status', 'legacy_code', 'movement', 'person_asked_by', 'person_executed_by',
                  'type_movement',
                  'delegation_date',
                  'acceptance_date', 'first_deadline_date', 'second_deadline_date', 'execution_date', 'return_date',
                  'refused_date']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastrados"
