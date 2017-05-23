import django_tables2 as tables
from django_tables2 import A

from .models import TypeMovement, Movement, LawSuit, Folder, Task, CourtDistrict


class TypeMovementTable(tables.Table):
    class Meta:
        model = TypeMovement
        fields = ['name', 'legacy_code', 'uses_wo']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentação cadastrados"


class MovementTable(tables.Table):
    class Meta:
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = ['legacy_code', 'law_suit', 'person_lawyer', 'type_movement']
        empty_text = "Não existem movimentações cadastrados"


class FolderTable(tables.Table):
    legacy_code = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': '_blank'}}, args=[A('pk')])
    class Meta:
        model = Folder
        fields = ['legacy_code', 'person_customer']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"


class LawSuitTable(tables.Table):
    class Meta:
        model = LawSuit
        fields = ['folder', 'person_lawyer']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"


class TaskTable(tables.Table):
    class Meta:
        model = Task
        fields = ['legacy_code', 'movement', 'person', 'type_movement', 'delegation_date',
                  'acceptance_date', 'deadline_date', 'final_deadline_date', 'execution_deadline_date']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastrados"


class CourtDistrictTable(tables.Table):
    model = CourtDistrict
    fields = ['name', 'state']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não existem comarcas cadastrados"
