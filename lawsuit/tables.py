import django_tables2 as tables

from .models import TypeMovement, Movement, LawSuit, Folder, Task


class TypeMovementTable(tables.Table):
    model = TypeMovement
    fields = ['name', 'legacy_code', 'uses_wo']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não existem tipos de movimentação cadastrados"


class MovementTable(tables.Table):
    model = Movement
    attrs = {"class": "table-striped table-bordered"}
    fields = ['legacy_code', 'law_suit', 'person_lawyer', 'type_movement']
    empty_text = "Não existem movimentações cadastrados"


class FolderTable(tables.Table):
    model = Folder
    fields = ['legacy_code', 'person_customer']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não existem pastas cadastrados"


class LawSuitTable(tables.Table):
    model = LawSuit
    fields = ['folder', 'person_lawyer']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não existem processos cadastrados"


class TaskTable(tables.Table):
    model = Task
    fields = ['legacy_code', 'movement', 'person', 'type_movement', 'delegation_date',
              'acceptance_date', 'deadline_date', 'final_deadline_date', 'execution_deadline_date']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não existem providências cadastrados"
