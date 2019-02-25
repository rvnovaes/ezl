from core.models import Person
from collections import OrderedDict
from django.db import transaction
from django.db.models import Q
from financial.models import CostCenter
from import_export import resources
from import_export.widgets import CharWidget, IntegerWidget
from import_export.results import RowResult, Result
from lawsuit.models import Folder, LawSuit, Movement, TypeMovement, CourtDistrict, CourtDivision, Organ, Instance, \
    TypeLawsuit, CourtDistrictComplement, City, State
from task.fields import CustomFieldImportExport
from task.instance_loaders import TaskModelInstanceLoader
from task.messages import *
from task.models import Task, TypeTask, TaskStatus
from task.utils import self_or_none, set_performance_place
from task.task_import import TRUE_FALSE_DICT, COLUMN_NAME_DICT, ImportFolder
from task.widgets import PersonAskedByWidget, TaskStatusWidget, DateTimeWidgetMixin, PersonCompanyRepresentative, TypeTaskByWidget
import logging

logger = logging.getLogger('resources')


def insert_incorrect_natural_key_message(row, key):
    return INCORRECT_NATURAL_KEY.format(COLUMN_NAME_DICT[key]['verbose_name'],
                                        COLUMN_NAME_DICT[key]['column_name'],
                                        row[key])


class TaskRowResult(RowResult):
    IMPORT_TYPE_WARNING = 'warning'

    def __init__(self):
        super().__init__()
        self.warnings = []


class TaskResult(Result):

    def __init__(self):
        super().__init__()
        self.totals = OrderedDict([(TaskRowResult.IMPORT_TYPE_NEW, 0),
                                   (TaskRowResult.IMPORT_TYPE_UPDATE, 0),
                                   (TaskRowResult.IMPORT_TYPE_DELETE, 0),
                                   (TaskRowResult.IMPORT_TYPE_SKIP, 0),
                                   (TaskRowResult.IMPORT_TYPE_WARNING, 0),
                                   (TaskRowResult.IMPORT_TYPE_ERROR, 0)])

    def row_warnings(self):
        return [(i + 1, row.warnings)
                for i, row in enumerate(self.rows) if row.warnings]

    def has_warnings(self):
        return bool(self.row_warnings())


class TaskResource(resources.ModelResource):
    movement = CustomFieldImportExport(column_name='movement', attribute='movement_id', saves_null_values=False,
                                       column_name_dict=COLUMN_NAME_DICT)
    task_number = CustomFieldImportExport(column_name='task_number', attribute='task_number', widget=IntegerWidget(),
                                          saves_null_values=True, column_name_dict=COLUMN_NAME_DICT)
    person_asked_by = CustomFieldImportExport(column_name='person_asked_by', attribute='person_asked_by',
                                              widget=PersonAskedByWidget(Person, 'legal_name'), saves_null_values=False,
                                              column_name_dict=COLUMN_NAME_DICT)
    person_company_representative = CustomFieldImportExport(column_name='person_company_representative',
                                                            attribute='person_company_representative',
                                                            widget=PersonCompanyRepresentative(Person, 'legal_name'),
                                                            saves_null_values=False,
                                                            column_name_dict=COLUMN_NAME_DICT)
    type_task = CustomFieldImportExport(column_name='type_task', attribute='type_task',
                                        widget=TypeTaskByWidget(TypeTask, 'name'), saves_null_values=False,
                                        column_name_dict=COLUMN_NAME_DICT)
    task_status = CustomFieldImportExport(column_name='task_status', attribute='task_status', widget=TaskStatusWidget(),
                                          column_name_dict=COLUMN_NAME_DICT, default=TaskStatus.REQUESTED.value)
    final_deadline_date = CustomFieldImportExport(column_name='final_deadline_date', attribute='final_deadline_date',
                                                  widget=DateTimeWidgetMixin(), saves_null_values=False,
                                                  column_name_dict=COLUMN_NAME_DICT)
    performance_place = CustomFieldImportExport(column_name='performance_place', attribute='performance_place',
                                                widget=CharWidget(), saves_null_values=False,
                                                column_name_dict=COLUMN_NAME_DICT)
    legacy_code = CustomFieldImportExport(column_name='legacy_code', attribute='legacy_code', widget=CharWidget(),
                                          saves_null_values=True, column_name_dict=COLUMN_NAME_DICT)
    system_prefix = CustomFieldImportExport(column_name='system_prefix', attribute='system_prefix',
                                            saves_null_values=False, column_name_dict=COLUMN_NAME_DICT)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.office = None
        self.create_user = None
        self.office_id = None
        self.default_type_movement = None
        self._meta.instance_loader_class = TaskModelInstanceLoader
        self.folder = None
        self.lawsuit = None
        self.movement = None
        self.current_line = 0

    class Meta:
        model = Task
        import_id_fields = ('task_number', 'legacy_code')

    @classmethod
    def get_row_result_class(self):
        """
        Returns the class used to store the result of a row import.
        """
        return TaskRowResult

    @classmethod
    def get_result_class(self):
        """
        Returns the class used to store the result of an import.
        """
        return TaskResult

    def validate_movement(self, row, row_errors):
        """
        Faz a validacao do grupo de colunas referente ao movement
        :param row: dict com os dados da linha que está sendo processada no momento
        :param row_errors: lista de erros do processo de importação. Lista cumulativa dos processos de validação de
        folder, lawsuit e movement
        :return: Movement instance or None
        """
        type_movement_name = row.get('type_movement', '')
        movement_legacy_code = row.get('movement_legacy_code', '')
        if type(movement_legacy_code) == float and movement_legacy_code.is_integer():
            movement_legacy_code = str(int(movement_legacy_code))
        if not (type_movement_name or movement_legacy_code):
            movement, created = Movement.objects.get_or_create(
                folder=self.folder,
                law_suit=self.lawsuit,
                type_movement=self.default_type_movement,
                office=self.office,
                defaults={'create_user': self.create_user,
                          'system_prefix': row['system_prefix']})
        else:
            type_movement = TypeMovement.objects.filter(name__unaccent__iexact=type_movement_name,
                                                        office_id=self.office_id).first()
            movement = None
            if movement_legacy_code:
                movement = Movement.objects.filter(legacy_code=movement_legacy_code,
                                                   system_prefix=row['system_prefix'],
                                                   folder=self.folder,
                                                   law_suit=self.lawsuit,
                                                   office_id=self.office_id).first()
            if not movement and type_movement:
                movement, created = Movement.objects.get_or_create(
                    folder=self.folder,
                    law_suit=self.lawsuit,
                    office=self.office,
                    type_movement=type_movement,
                    legacy_code=movement_legacy_code,
                    defaults={'system_prefix': row['system_prefix'],
                              'create_user': self.create_user})
            elif not movement and not type_movement:
                row_errors.append(insert_incorrect_natural_key_message(row, 'type_movement'))
        if not movement:
            row_errors.append(RECORD_NOT_FOUND.format(Movement._meta.verbose_name))
        return movement

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.office = kwargs['office']
        self.create_user = kwargs['create_user']
        self.office_id = self.office.id
        for k, v in COLUMN_NAME_DICT.items():
            if v['column_name'] in dataset.headers:
                headers_index = dataset.headers.index(v['column_name'])
                dataset.headers[headers_index] = k

        self.default_type_movement, created = TypeMovement.objects.get_or_create(
            is_default=True,
            office=self.office,
            defaults={
                'name': 'OS Avulsa',
                'create_user': self.create_user
            })
        dataset.insert_col(0, col=["", ] * dataset.height, header="id")
        dataset.insert_col(1, col=[int("{}".format(self.office.id)), ] * dataset.height, header="office")
        dataset.insert_col(2, col=[int("{}".format(self.create_user.id)), ] * dataset.height, header="create_user")
        dataset.insert_col(3, col=["", ] * dataset.height, header="movement")
        dataset.insert_col(dataset.width, col=[[], ] * dataset.height, header="warnings")

    def before_import_row(self, row, **kwargs):
        row_errors = []
        row['warnings'] = []
        instance = None
        row['task_number'] = self_or_none(row['task_number'])
        row['legacy_code'] = self_or_none(row['legacy_code'])
        row['is_active'] = TRUE_FALSE_DICT.get('is_active', True)
        if row['task_number'] or row['legacy_code']:
            instance_loader = self._meta.instance_loader_class(self, row)
            instance = self.get_instance(instance_loader, row)
        if not instance:
            with transaction.atomic():
                self.folder = ImportFolder(row, row_errors, self.office, self.create_user).get_folder()
                self.lawsuit = self.validate_lawsuit(row, row_errors) if self.folder else None
                self.movement = self.validate_movement(row, row_errors) if self.lawsuit else None

                if self.movement:
                    row['movement'] = self.movement.id
                if not row.get('performance_place', None) and self.movement:
                    row['performance_place'] = set_performance_place(self.movement)
                if row_errors:
                    transaction.set_rollback(True)
                    raise Exception(row_errors)
        else:
            row['id'] = instance.id
            row['task_status'] = instance.task_status
            row['movement'] = instance.movement.id            
            if not row['performance_place']:
                row['performance_place'] = instance.performance_place

    def after_import_row(self, row, row_result, **kwargs):
        line_warnings = row['warnings']
        if line_warnings:
            for warning in line_warnings:
                row_result.warnings.append(warning)
            row_result.import_type = TaskRowResult.IMPORT_TYPE_WARNING

    def skip_row(self, instance, original):
        if instance.task_status not in [TaskStatus.REQUESTED.value, TaskStatus.ACCEPTED_SERVICE.value]:
            return True
        return super().skip_row(instance, original)
