from core.models import Person
from django.core.exceptions import ObjectDoesNotExist
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DecimalWidget
from lawsuit.models import Folder, LawSuit, Movement
from task.models import Task, TypeTask
from task.widgets import PersonAskedByWidget, UnaccentForeignKeyWidget, TaskStatusWidget


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
                                widget=DateTimeWidget(format='%d/%m/%Y %H:%M'),
                                saves_null_values=False)
    delegation_date = Field(column_name='delegation_date', attribute='delegation_date',
                            widget=DateTimeWidget(format='%d/%m/%Y %H:%M'))
    acceptance_date = Field(column_name='acceptance_date', attribute='acceptance_date',
                            widget=DateTimeWidget(format='%d/%m/%Y %H:%M'))
    execution_date = Field(column_name='execution_date', attribute='execution_date',
                           widget=DateTimeWidget(format='%d/%m/%Y %H:%M'))
    requested_date = Field(column_name='requested_date', attribute='requested_date',
                           widget=DateTimeWidget(format='%d/%m/%Y %H:%M'))
    task_status = Field(column_name='task_status', attribute='task_status', widget=TaskStatusWidget())
    amount = Field(column_name='amount', attribute='amount', widget=DecimalWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.office_id = None

    class Meta:
        model = Task

    def validate_folder(self, row, row_errors):
        folder_number = int(row['folder_number']) if row['folder_number'] else ''
        folder_legacy_code = row['folder_legacy_code']
        folder = None
        if not (folder_legacy_code or folder_number):
            row_errors.append(ValueError("É obrigatório o preenchimento de um dos campos de identificação da pasta "
                                         "(folder_number ou folder_legacy_code"))
        else:
            if folder_legacy_code:
                folder = Folder.objects.filter(legacy_code=folder_legacy_code, office_id=self.office_id).first()
            if not folder and folder_number:
                folder = Folder.objects.filter(folder_number=folder_number, office_id=self.office_id).first()
            if not folder:
                row_errors.append(ObjectDoesNotExist('Não foi encontrado registro de pasta correspondente aos valores '
                                                     'informados'))
        return folder

    def validate_lawsuit(self, row, row_errors):
        lawsuit_number = row['law_suit_number']
        lawsuit_legacy_code = row['lawsuit_legacy_code']
        instance = row['instance']
        lawsuit = None
        if not (lawsuit_legacy_code or lawsuit_number) or not instance:
            row_errors.append(ValueError("É obrigatório o preenchimento de um dos campos de identificação do processo "
                                         "(lawsuit_number ou lawsuit_legacy_code, além do campo de instância"))
        else:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(legacy_code=lawsuit_legacy_code, office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                lawsuit = LawSuit.objects.filter(law_suit_number=lawsuit_number, office_id=self.office_id).first()
            if not lawsuit:
                row_errors.append(ObjectDoesNotExist('Não foi encontrado registro de processo correspondente aos '
                                                     'valores informados'))
        return lawsuit

    def validate_movement(self, row, row_errors, folder, lawsuit):
        type_movement_name = row['type_movement']
        movement_legacy_code = row['movement_legacy_code']
        movement = None
        if not (type_movement_name or movement_legacy_code):
            row_errors.append(ValueError("É obrigatório o preenchimento de um dos campos de identificação da "
                                         "movimentação (type_movement ou movement_legacy_code)"))
        else:
            if movement_legacy_code:
                movement = Movement.objects.filter(legacy_code=movement_legacy_code, office_id=self.office_id).first()
            if not movement and (type_movement_name and folder and lawsuit):
                movement = Movement.objects.filter(folder=folder, law_suit=lawsuit,
                                                   type_movement__name=type_movement_name, office_id=self.office_id
                                                   ).first()
            if not movement:
                row_errors.append(ObjectDoesNotExist('Não foi encontrado registro de movimentação com os '
                                                     'valores informados'))
        return movement

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
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
            # final_deadline = row['final_deadline_date']
            # seconds = int(round((final_deadline - 25569) * 86400.0))
            # final_deadline = make_aware(datetime.datetime.utcfromtimestamp(seconds))
            # row['final_deadline_date'] = final_deadline
        if row_errors:
            raise Exception(row_errors)
