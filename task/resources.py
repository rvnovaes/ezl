from core.models import Person
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DecimalWidget
from lawsuit.models import Folder, LawSuit, Movement
from task.models import Task, TypeTask
from task.widgets import PersonAskedByWidget, UnaccentForeignKeyWidget, TaskStatusWidget


COLUMN_NAME_DICT = {
    'folder_number': {'column_name': 'Número da Pasta', 'attribute': 'folder_number'},
    'folder_legacy_code': {'column_name': 'Código legado da pasta', 'attribute': 'movement__folder__legacy_code'},
    'law_suit_number': {'column_name': 'Número do processo', 'attribute': 'movement__law_suit__law_suit_number'},
    'instance': {'column_name': 'Instância', 'attribute': 'movement__law_suit__instance__name'},
    'lawsuit_legacy_code': {'column_name': 'Código legado do processo', 'attribute': 'movement__law_suit__legacy_code'},
    'type_movement': {'column_name': 'Tipo de movimentação', 'attribute': 'movement__type_movement__name'},
    'movement_legacy_code': {'column_name': 'Código legado da movimentação', 'attribute': 'movement__legacy_code'},
    'person_asked_by': {'column_name': 'Solicitante', 'attribute': 'person_asked_by'},
    'type_task': {'column_name': 'Tipo de serviço', 'attribute': 'type_task'},
    'final_deadline_date': {'column_name': 'Prazo fatal', 'attribute': 'final_deadline_date'},
    'description': {'column_name': 'Descrição do serviço', 'attribute': 'description'},
    'person_executed_by': {'column_name': 'Correspondente', 'attribute': 'person_executed_by'},
    'person_distributed_by': {'column_name': 'Contratante', 'attribute': 'person_distributed_by'},
    'delegation_date': {'column_name': 'Data da delegação', 'attribute': 'delegation_date'},
    'execution_date': {'column_name': 'Data do cumprimento', 'attribute': 'execution_date'},
    'requested_date': {'column_name': 'Data da solicitação', 'attribute': 'requested_date'},
    'acceptance_date': {'column_name': 'Data do aceite', 'attribute': 'acceptance_date'},
    'task_status': {'column_name': 'Status da OS', 'attribute': 'task_status'},
    'amount': {'column_name': 'Valor do serviço', 'attribute': 'amount'},
    'legacy_code': {'column_name': 'Código legado', 'attribute': 'legacy_code'},
}


class TaskResource(resources.ModelResource):

    type_task = Field(column_name='type_task', attribute='type_task', widget=UnaccentForeignKeyWidget(TypeTask, 'name'),
                      saves_null_values=False)
    person_asked_by = Field(column_name='person_asked_by', attribute='person_asked_by',
                            widget=PersonAskedByWidget(Person, 'legal_name'), saves_null_values=False)
    person_executed_by = Field(column_name='person_executed_by', attribute='person_executed_by',
                               widget=UnaccentForeignKeyWidget(Person, 'legal_name'))
    person_distributed_by = Field(column_name='person_distributed_by', attribute='person_distributed_by',
                                  widget=UnaccentForeignKeyWidget(Person, 'legal_name'))
    final_deadline_date = Field(column_name='final_deadline_date', attribute='final_deadline_date',
                                widget=DateTimeWidget(),
                                saves_null_values=False)
    delegation_date = Field(column_name='delegation_date', attribute='delegation_date',
                            widget=DateTimeWidget())
    acceptance_date = Field(column_name='acceptance_date', attribute='acceptance_date',
                            widget=DateTimeWidget())
    execution_date = Field(column_name='execution_date', attribute='execution_date',
                           widget=DateTimeWidget())
    requested_date = Field(column_name='requested_date', attribute='requested_date',
                           widget=DateTimeWidget())
    task_status = Field(column_name='task_status', attribute='task_status', widget=TaskStatusWidget())
    amount = Field(column_name='amount', attribute='amount', widget=DecimalWidget(), default=Decimal('0.00'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.office_id = None

    class Meta:
        model = Task
        import_id_fields = ('id', 'legacy_code',)

    def validate_folder(self, row, row_errors):
        folder_number = int(row['folder_number']) if row['folder_number'] else ''
        folder_legacy_code = row['folder_legacy_code']
        folder = None
        if not (folder_legacy_code or folder_number):
            row_errors.append("É obrigatório o preenchimento de um dos campos de identificação da pasta "
                              "(folder_number ou folder_legacy_code);")
        else:
            if folder_legacy_code:
                folder = Folder.objects.filter(legacy_code=folder_legacy_code, office_id=self.office_id).first()
            if not folder and folder_number:
                folder = Folder.objects.filter(folder_number=folder_number, office_id=self.office_id).first()
            if not folder:
                row_errors.append('Não foi encontrado registro de pasta correspondente aos valores informados;')
        return folder

    def validate_lawsuit(self, row, row_errors):
        lawsuit_number = row['law_suit_number']
        lawsuit_legacy_code = row['lawsuit_legacy_code']
        instance = row['instance']
        lawsuit = None
        if not (lawsuit_legacy_code or lawsuit_number) or not instance:
            row_errors.append("É obrigatório o preenchimento de um dos campos de identificação do processo "
                              "(lawsuit_number ou lawsuit_legacy_code, além do campo de instância);")
        else:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(legacy_code=lawsuit_legacy_code, office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                lawsuit = LawSuit.objects.filter(law_suit_number=lawsuit_number, office_id=self.office_id).first()
            if not lawsuit:
                row_errors.append('Não foi encontrado registro de processo correspondente aos valores informados;')
        return lawsuit

    def validate_movement(self, row, row_errors, folder, lawsuit):
        type_movement_name = row['type_movement']
        movement_legacy_code = row['movement_legacy_code']
        movement = None
        if not (type_movement_name or movement_legacy_code):
            row_errors.append("É obrigatório o preenchimento de um dos campos de identificação da "
                              "movimentação (type_movement ou movement_legacy_code);")
        else:
            if movement_legacy_code:
                movement = Movement.objects.filter(legacy_code=movement_legacy_code, office_id=self.office_id).first()
            if not movement and (type_movement_name and folder and lawsuit):
                movement = Movement.objects.filter(Q(folder=folder), Q(law_suit=lawsuit),
                                                   Q(type_movement__name=type_movement_name),
                                                   Q(office_id=self.office_id)).first()
            if not movement:
                row_errors.append('Não foi encontrado registro de movimentação com os valores informados;')
        return movement

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        for k, v in COLUMN_NAME_DICT.items():
            if v['column_name'] in dataset.headers:
                headers_index = dataset.headers.index(v['column_name'])
                dataset.headers[headers_index] = k

        if 'id' not in dataset._Dataset__headers:
            dataset.insert_col(0, col=["", ] * dataset.height, header="id")
        dataset.insert_col(1, col=[int("{}".format(kwargs['office'].id)), ] * dataset.height, header="office")
        dataset.insert_col(1, col=[int("{}".format(kwargs['create_user'].id)), ] * dataset.height, header="create_user")
        dataset.insert_col(3, col=["", ] * dataset.height, header="movement")

    def before_import_row(self, row, **kwargs):
        row_errors = []
        self.office_id = row['office']
        folder = self.validate_folder(row, row_errors)
        lawsuit = self.validate_lawsuit(row, row_errors)
        movement = self.validate_movement(row, row_errors, folder, lawsuit)

        if movement:
            row['movement'] = movement.id
        if row_errors:
            raise Exception(row_errors)

