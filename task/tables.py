import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from task.models import Task


class TaskTable(tables.Table):
    def __init__(self, *args, _overriden_value="Estado", **kwargs):
        super().__init__(*args, **kwargs)

        self.base_columns['status'].verbose_name = _overriden_value

    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    legacy_code = tables.LinkColumn(viewname='task_update', attrs={'a': {'target': 'task_update'}}, args=[A('pk')])

    status = tables.TemplateColumn(template_name="task/task_status_column.html")

    class Meta:
        model = Task
        fields = ['selection', 'status', 'legacy_code', 'movement', 'person_asked_by', 'person_executed_by',
                  'type_movement',
                  'delegation_date',
                  'acceptance_date', 'first_deadline_date', 'second_deadline_date', 'execution_date', 'return_date',
                  'refused_date']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastradas"


class DashboardStatusTable(tables.Table):
    def __init__(self, *args, service="Serviço", client="Cliente", legacy_code="Número", title="tabela", **kwargs):
        super().__init__(*args, **kwargs)

        self.base_columns['service'].verbose_name = service
        self.base_columns['client'].verbose_name = client
        self.base_columns['legacy_code'].verbose_name = legacy_code
        self.title = title

    legacy_code = tables.LinkColumn(viewname='task_detail', attrs={'a': {'target': 'task_detail'}}, args=[A('pk')])

    class Meta:
        model = Task
        fields = ['legacy_code', 'service', 'first_deadline_date', 'client']
        empty_text = "Não existem providências a serem exibidas"
