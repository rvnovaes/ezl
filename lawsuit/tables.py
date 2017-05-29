import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from .models import TypeMovement, Movement, LawSuit, Folder, CourtDistrict


class TypeMovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'type_movement_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'name', 'uses_wo')
        model = TypeMovement
        fields = ['selection', 'name', 'legacy_code', 'uses_wo']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentação cadastrados"


class MovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'movement_update'}},
                                    args=[A('pk')])

    class Meta:
        sequence = ('selection', 'law_suit', 'person_lawyer', 'type_movement')
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = ['selection', 'legacy_code', 'law_suit', 'person_lawyer', 'type_movement']
        empty_text = "Não existem movimentações cadastrados"


class FolderTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'folder_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'person_customer', '...')
        model = Folder
        fields = ['selection', 'legacy_code', 'person_customer']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"


class LawSuitTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'folder', 'person_lawyer')
        model = LawSuit
        fields = ['selection', 'folder', 'person_lawyer']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"


class CourtDistrictTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'courtdistrict_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'state')
        model = CourtDistrict
        fields = ['selection', 'name', 'state']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem comarcas cadastrados"
