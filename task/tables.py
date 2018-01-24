import django_tables2 as tables
from core.tables import CheckBoxMaterial
from .models import TypeTask, DashboardViewModel, Filter


class TaskTable(tables.Table):

    def __init__(self, *args, _overriden_value="Estado", **kwargs):
        super().__init__(*args, **kwargs)

        self.base_columns['status'].verbose_name = _overriden_value
        self.length = self.rows.__len__()

    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    status = tables.TemplateColumn(template_name="task/task_status_column.html",
                                   orderable=False)

    delegation_date = tables.DateColumn(format="d/m/Y")
    acceptance_date = tables.DateColumn(format="d/m/Y")
    final_deadline_date = tables.DateTimeColumn(short=True)
    execution_date = tables.DateColumn(format="d/m/Y")
    return_date = tables.DateColumn(format="d/m/Y")
    refused_date = tables.DateColumn(format="d/m/Y")

    class Meta:
        order_by = 'legal_name'
        model = DashboardViewModel
        sequence = ['selection', 'status', 'task_number', 'type_task', "person_executed_by", 'person_asked_by',
                    "final_deadline_date", 'delegation_date', 'acceptance_date', 'refused_date',
                    'execution_date', 'return_date', 'blocked_payment_date', 'finished_date',
                    'is_active']
        fields = ['selection', 'status', 'task_number', 'person_asked_by', 'person_executed_by', 'type_task',
                  'delegation_date', 'acceptance_date', 'final_deadline_date', 'execution_date',
                  'return_date', 'refused_date', 'legacy_code', 'blocked_payment_date',
                  'finished_date', 'is_active']
        empty_text = "Não existem providências cadastradas"
        row_attrs = {
            'data_href': lambda record: '/providencias/providencias/' + str(
                record.movement.id) + '/' + str(record.pk) + '/'
        }


class DashboardStatusTable(tables.Table):
    def __init__(self, *args, delegation_date='Delegação', client="Cliente",
                 lawsuit_number="Processo", type_service="Serviço", opposing_party="Parte adversa",
                 title="", status="", **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns['delegation_date'].verbose_name = delegation_date
        self.base_columns['client'].verbose_name = client
        self.base_columns['lawsuit_number'].verbose_name = lawsuit_number
        self.base_columns['type_service'].verbose_name = type_service
        self.base_columns['opposing_party'].verbose_name = opposing_party
        self.base_columns['task_number'].verbose_name = 'Número da OS'
        self.title = title
        self.status = status

        self.length = self.rows.__len__()

    client = tables.Column(orderable=True)
    type_service = tables.Column(orderable=True)

    class Meta:
        model = DashboardViewModel
        fields = ['task_number', 'final_deadline_date', 'type_service', 'lawsuit_number', 'client',
                  'opposing_party', 'delegation_date', 'legacy_code']
        empty_text = "Não existem providências a serem exibidas"
        row_attrs = {
            'data_new_href': lambda record: '/dashboard/' + str(record.pk) + '/'
        }
        order_by = ('-final_deadline_date', )


class TypeTaskTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'survey', 'is_active', 'legacy_code')
        model = TypeTask
        fields = ['selection', 'legacy_code', 'name', 'is_active', 'survey']
        empty_text = "Não existem tipos de serviço cadastrados"
        row_attrs = {
            'data_href': lambda record: '/providencias/tipo_servico/' + str(record.pk) + '/'
        }


class FilterTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'description')
        model = Filter
        fields = ['selection', 'name', 'description']
        empty_text = "Não existem filtros cadastrados"
        row_attrs = {
            'data_href': lambda record: '/providencias/filtros/' + str(record.pk) + '/'
        }
        order_by = ('-name',)
