import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from .models import Task, TypeTask


class TaskTable(tables.Table):
    def __init__(self, *args, _overriden_value="Estado", **kwargs):
        super().__init__(*args, **kwargs)

        self.base_columns['status'].verbose_name = _overriden_value
        self.length = self.rows.__len__()

    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    type_task = tables.LinkColumn(viewname='task_update', attrs={'a': {'target': 'task_update'}},
                                  args=[A('movement.id'), A('pk')])

    status = tables.TemplateColumn(template_name="task/task_status_column.html",
                                   orderable=False)

    delegation_date = tables.DateColumn(format="d/m/Y")
    acceptance_date = tables.DateColumn(format="d/m/Y")
    reminder_deadline_date = tables.DateColumn(format="d/m/Y")
    final_deadline_date = tables.DateColumn(format="d/m/Y")
    execution_date = tables.DateColumn(format="d/m/Y")
    return_date = tables.DateColumn(format="d/m/Y")
    refused_date = tables.DateColumn(format="d/m/Y")

    # order_by = sorted(Task.objects.all(), key=lambda t: str(t.status.value))

    class Meta:
        model = Task
        fields = ['selection', 'type_task', 'status', 'movement', 'person_asked_by', 'person_executed_by',

                  'delegation_date',
                  'acceptance_date', 'reminder_deadline_date', 'final_deadline_date', 'execution_date', 'return_date',
                  'refused_date', 'legacy_code']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastradas"


class DashboardStatusTable(tables.Table):
    def __init__(self, *args, delegation_date='Delegação', reminder_deadline_date='Prazo', service="Serviço",
                 client="Cliente", legacy_code="Número",
                 title="", status="",
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns['type_task'].verbose_name = service
        self.base_columns['client'].verbose_name = client
        self.base_columns['legacy_code'].verbose_name = legacy_code
        self.base_columns['reminder_deadline_date'].verbose_name = reminder_deadline_date
        self.base_columns['delegation_date'].verbose_name = delegation_date
        self.title = title
        self.status = status
        self.order_by = '-alter_date'
        self.length = self.rows.__len__()

    legacy_code = tables.LinkColumn(viewname='task_detail', attrs={'a': {'target': 'task_detail'}}, args=[A('pk')])

    client = tables.Column(orderable=False)

    class Meta:
        model = Task
        fields = ['legacy_code', 'type_task', 'delegation_date', 'reminder_deadline_date', 'client']
        empty_text = "Não existem providências a serem exibidas"


class TypeTaskTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    legacy_code = tables.LinkColumn(viewname='typetask_update', attrs={'a': {'target': 'typetask_update'}},
                                    args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'name', 'survey_type', 'is_active')
        model = TypeTask
        fields = ['selection', 'legacy_code', 'name', 'is_active', 'survey_type']
        empty_text = "Não existem tipos de serviço cadastrados"
