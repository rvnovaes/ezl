import datetime
from core.models import Person
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware
from import_export import resources
from import_export.fields import Field
from import_export.widgets import Widget, IntegerWidget
from lawsuit.models import Folder, LawSuit, Movement
from task.models import Task, TypeTask


class FolderNumberWidget(Widget):
    """
    Widget for validate folder_number field.
    """

    def clean(self, value, row=None, *args, **kwargs):
        # if self.is_empty(value):
        #     raise ValueError("Campo Número da pasta não pode ser vazio.")
        raise ValueError("Estaria certo, mas sou chato.") # return int(float(value))


class TaskResource(resources.ModelResource):
    folder_number = Field(attribute='folder_number', column_name='folder_number', widget=FolderNumberWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.office_id = None

    class Meta:
        model = Task

    def validate_folder(self, row, row_errors):
        folder_number = int(row['folder_number'])
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
        lawsuit_number = int(row['lawsuit_number'])
        lawsuit_legacy_code = row['lawsuit_legacy_code']
        instance = row['instance']
        lawsuit = None
        if not (lawsuit_legacy_code or lawsuit_number) and not instance:
            row_errors.append(ValueError("É obrigatório o preenchimento de um dos campos de identificação do processo "
                                         "(lawsuit_number ou lawsuit_legacy_code, além do campo de instância"))
        else:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(legacy_code=lawsuit_legacy_code, office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                folder = Folder.objects.filter(lawsuit_number=lawsuit_number, office_id=self.office_id).first()
            if not lawsuit:
                row_errors.append(ObjectDoesNotExist('Não foi encontrado registro de processo correspondente aos '
                                                     'valores informados'))
        return lawsuit

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'id' not in dataset._Dataset__headers:
            dataset.insert_col(0, col=["", ] * dataset.height, header="id")
        dataset.insert_col(1, col=[int("{}".format(kwargs['office'].id)), ] * dataset.height, header="office")
        dataset.insert_col(1, col=[int("{}".format(kwargs['create_user'].id)), ] * dataset.height, header="create_user")
        dataset.insert_col(3, col=["", ] * dataset.height, header="movement")

    def before_import_row(self, row, **kwargs):
        from pudb import set_trace;
        set_trace()
        row_errors = []
        self.office_id = row['office']
        folder = self.validate_folder(row, row_errors)
        lawsuit = self.validate_lawsuit(row, row_errors)

        type_movement_name = row['type_movement']
        movement = Movement.objects.filter(folder=folder, law_suit=lawsuit,
                                           type_movement__name=type_movement_name).first()
        row['movement'] = movement.id
        person_asked_by = Person.objects.filter(legal_name=row['person_asked_by']).first()
        if person_asked_by in Person.objects.requesters(office_id=self.office_id):
            row['person_asked_by'] = person_asked_by.id
        type_task = TypeTask.objects.filter(name__unaccent__iexact=row['type_task']).first()
        row['type_task'] = type_task.id
        final_deadline = row['final_deadline_date']
        seconds = int(round((final_deadline - 25569) * 86400.0))
        final_deadline = make_aware(datetime.datetime.utcfromtimestamp(seconds))
        row['final_deadline_date'] = final_deadline
        if row_errors:
            raise Exception(row_errors)
