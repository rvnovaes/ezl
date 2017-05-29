import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from task.models import Task


class TaskTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    legacy_code = tables.LinkColumn(viewname='task_update', attrs={'a': {'target': 'task_update'}}, args=[A('pk')])

    class Meta:
        model = Task
        fields = ['selection', 'legacy_code', 'movement', 'person_asked_by', 'person_executed_by', 'type_movement',
                  'delegation_date',
                  'acceptance_date', 'first_deadline_date', 'second_deadline_date', 'execution_date', 'return_date',
                  'refused_date']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastrados"
