import datetime
from core.models import Person
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
    movement = Field(attribute='movement', column_name='movement', widget=FolderNumberWidget())

    class Meta:
        model = Task

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'id' not in dataset._Dataset__headers:
            dataset.insert_col(0, col=["", ] * dataset.height, header="id")
        dataset.insert_col(1, col=[int("{}".format(kwargs['office'].id)), ] * dataset.height, header="office")
        dataset.insert_col(1, col=[int("{}".format(kwargs['create_user'].id)), ] * dataset.height, header="create_user")
        dataset.insert_col(3, col=["", ] * dataset.height, header="movement")

    def before_import_row(self, row, **kwargs):
        from pudb import set_trace;
        set_trace()
        folder_number = int(row['folder_number'])
        office = row['office']
        type_movement_name = row['type_movement']
        law_suit_number = row['law_suit_number']
        folder = Folder.objects.filter(folder_number=folder_number, office_id=office).first()
        lawsuit = LawSuit.objects.filter(folder=folder, law_suit_number=law_suit_number).first()
        movement = Movement.objects.filter(folder=folder, law_suit=lawsuit,
                                           type_movement__name=type_movement_name).first()
        row['movement'] = movement.id
        person_asked_by = Person.objects.filter(legal_name=row['person_asked_by']).first()
        if person_asked_by in Person.objects.requesters(office_pk=office):
            row['person_asked_by'] = person_asked_by.id
        type_task = TypeTask.objects.filter(name__unaccent__iexact=row['type_task']).first()
        row['type_task'] = type_task.id
        final_deadline = row['final_deadline_date']
        seconds = int(round((final_deadline - 25569) * 86400.0))
        final_deadline = make_aware(datetime.datetime.utcfromtimestamp(seconds))
        row['final_deadline_date'] = final_deadline
